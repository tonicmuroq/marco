# coding: utf-8

import json
import logging
from urllib2 import quote
from werkzeug import cached_property

from marco.ext import db, etcd, influxdb
from marco.models.consts import TaskStatus
from marco.models.base import Base

from marco.utils import yaml_loads

METRICS = {
    'cpu_usage', 'cpu_user', 'cpu_system',
    'mem_usage', 'mem_rss',
    'net_recv', 'net_send', 'net_recv_err',
    'net_send_err',
}


class Application(Base):

    __tablename__ = 'application'

    name = db.Column(db.String(255), nullable=False)
    pname = db.Column(db.String(255), nullable=False)
    namespace = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_by_name(cls, name):
        u"""获取确定的一个app, 如果有多个就挂"""
        return db.session.query(cls).filter(cls.name == name).one()

    @classmethod
    def get_all_app_names(cls, start=0, limit=20):
        u"""取所有的应用名字, 从start开始取limit个"""
        q = db.session.query(cls.name).order_by(cls.name.asc()).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return [r for r, in q.all()]

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

    def tasks(self, status=None, succ=None, start=0, limit=20):
        from .task import Job 
        return Job.get_multi(self.name, status=status, succ=succ, start=start, limit=limit)

    def processing_tasks(self, start=0, limit=20):
        return self.tasks(status=TaskStatus.Running, start=start, limit=limit)

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
            sql = ("select mean(value) from %s where "
                   "metric='%s' group by time(%ds) limit %d" %
                   (self.name, metric, time, limit))
            return influxdb.query(sql)[0]
        except StandardError, e:
            logging.exception(e)
            return {'data': [], 'name': ''}

class AppVersion(Base):

    __tablename__ = 'app_version'

    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime)
    image_addr = db.Column(db.String(255), nullable=False)

    @classmethod
    def get(cls, id):
        return db.session.query(cls).filter(cls.id == id).one()

    @classmethod
    def get_by_name_and_version(cls, name, version):
        return db.session.query(cls).filter(cls.name == name, cls.version == version).one()

    @classmethod
    def get_multi(cls, name):
        return db.session.query(cls).filter(cls.name == name).order_by(cls.created.desc()).all()

    @cached_property
    def app_yaml(self):
        try:
            r = etcd.get('/NBE/{self.name}/{self.version}/app.yaml'.format(self=self))
            app_yaml = r.value if (r and not r.dir) else '{}'
        except KeyError:
            app_yaml = '{}'
        return yaml_loads(app_yaml)

    def tasks(self, status=None, succ=None, start=0, limit=20):
        from .task import Job 
        return Job.get_multi(self.name, self.version, status=status, succ=succ, start=start, limit=limit)

    def processing_tasks(self, start=0, limit=20):
        return self.tasks(status=TaskStatus.Running, start=start, limit=limit)

    def processing(self):
        return len(self.processing_tasks(limit=1)) > 0

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
    return yaml_loads(config)
