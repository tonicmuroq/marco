# coding: utf-8

import json
import logging
import arrow
import yaml
from urllib2 import quote
from werkzeug import cached_property

from marco.ext import dot, etcd, influxdb
from marco.models.consts import TaskStatus

from marco.utils import yaml_loads

METRICS = {
    'cpu_usage', 'cpu_user', 'cpu_system',
    'mem_usage', 'mem_rss',
    'net_recv', 'net_send', 'net_recv_err',
    'net_send_err',
}


class Application(object):

    def __init__(self, id, name, pname, namespace):
        self.id = id
        self.name = name
        self.pname = pname
        self.namespace = namespace

    @classmethod
    def get_by_name(cls, name):
        u"""获取确定的一个app, 如果有多个就挂"""
        app = dot.get_app(name)
        if app:
            return cls(**app)

    @classmethod
    def get_all_app_names(cls, start=0, limit=200):
        u"""取所有的应用名字, 从start开始取limit个"""
        apps = dot.get_apps(start, limit)
        return [a['name'] for a in apps]

    def mysql_args_dict(self):
        key = '/NBE/{self.name}/mysql'.format(self=self)
        r = etcd.get(key)
        r = r.value if (r and not r.dir) else '{}'
        return json.loads(r)

    @property
    def gitlab_id(self):
        return quote('%s/%s' % (self.namespace, self.pname), safe='')

    def all_versions(self):
        return AppVersion.get_multi(self.name)

    def tasks(self, status=-1, succ=-1, start=0, limit=20):
        from .task import Job 
        return Job.get_multi(self.name, status=status, succ=succ, start=start, limit=limit)

    def processing_tasks(self, start=0, limit=20):
        return self.tasks(status=TaskStatus.Running.value, start=start, limit=limit)

    def processing(self):
        return len(self.processing_tasks(limit=1)) > 0

    def git_repo_url(self):
        return 'http://git.hunantv.com/{self.group}/{self.pname}'.format(self=self)

    def online_url(self):
        return 'http://{self.name}.intra.hunantv.com'.format(self=self)

    def all_realtime_metric_data(self, time, limit):
        return {m: self.realtime_metric_data(m, time, limit) for m in METRICS}

    def realtime_metric_data(self, metric='cpu_usage', time=10, limit=100):
        try:
            if metric not in METRICS:
                raise ValueError('Unexpected metric')
            sql = ("select mean(value) from \"%s\" where "
                   "metric='%s' group by time(%ds) limit %d" %
                   (self.name, metric, time, limit))
            return influxdb.query(sql)[0]
        except StandardError, e:
            logging.exception(e)
            return {'data': [], 'name': ''}

    @property
    def zipkin_rate(self):
        try:
            r = etcd.get('/sample/%s' % self.name)
            return int(r.value)
        except:
            return 0
        
    @zipkin_rate.setter
    def zipkin_rate(self, v):
        try:
            etcd.set('/sample/%s' % self.name, v)
        except:
            pass

class AppVersion(object):

    def __init__(self, id, name, version, created, image_addr, app_yaml):
        self.id = id
        self.name = name
        self.version = version
        self.created = arrow.get(created).datetime
        self.image_addr = image_addr
        self.app_yaml = app_yaml

    @classmethod
    def _init(cls, **kw):
        kw['app_yaml'] = kw.pop('app.yaml')
        return cls(**kw)

    @classmethod
    def get(cls, id):
        av = dot.get_appversion_by_id(id)
        if av:
            return cls._init(**av)

    @classmethod
    def get_by_name_and_version(cls, name, version):
        av = dot.get_appversion(name, version)
        if av:
            return cls._init(**av)

    @classmethod
    def get_multi(cls, name, start=0, limit=20):
        avs = dot.get_app_versions(name, start=start, limit=limit)
        return [cls._init(**av) for av in avs if av]

    def tasks(self, status=-1, succ=-1, start=0, limit=20):
        from .task import Job 
        return Job.get_multi(self.name, self.version, status=status, succ=succ, start=start, limit=limit)

    def processing_tasks(self, start=0, limit=20):
        return self.tasks(status=TaskStatus.Running.value, start=start, limit=limit)

    def processing(self):
        return len(self.processing_tasks(limit=1)) > 0

    @property
    def gitlab_id(self):
        return self.application.gitlab_id

    @cached_property
    def application(self):
        return Application.get_by_name(self.name)

    @cached_property
    def runtime(self):
        return self.app_yaml['runtime']

    @cached_property
    def containers(self):
        u"""应用的所有container"""
        from .container import Container
        return Container.get_multi(app_name=self.name, version=self.version)

    @cached_property
    def n_container(self):
        u"""container数量"""
        return len(self.containers)

    @cached_property
    def hosts(self):
        u"""这个应用所处的host"""
        from .host import Host
        host_ids = list(set(c.host_id for c in self.containers))
        return filter(None, [Host.get(i) for i in host_ids])


def get_config_yaml(app_name, env):
    try:
        r = etcd.get('/NBE/%s/resource-%s' % (app_name, env))
        config = r.value if (r and not r.dir) else '{}'
    except KeyError:
        config = '{}'
    if not config:
        config = '{}'
    return yaml_loads(config)


def set_config_yaml(app_name, env, config):
    try:
        etcd.set('/NBE/%s/resource-%s' % (app_name, env), yaml.safe_dump(config, default_flow_style=False))
        return True
    except:
        return False
