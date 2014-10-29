# coding: utf-8

from urllib2 import quote
from werkzeug import cached_property

from marco.ext import db, etcd, influxdb
from marco.models.consts import TaskStatus
from marco.models.base import Base

from marco.utils import yaml_loads


class Application(Base):

    __tablename__ = 'application'

    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    pname = db.Column(db.String(255), nullable=False)
    group = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime)
    image_addr = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_by_name_and_version(cls, name, version):
        '''获取确定的一个app, 如果有多个就挂'''
        return db.session.query(cls).filter(cls.name == name, cls.version == version).one()

    @classmethod
    def get_all_app_names(cls, start=0, limit=20):
        '''取所有的应用名字, 从start开始取limit个'''
        q = db.session.query(cls.name).distinct(cls.name).order_by(cls.name.asc()).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return [r for r, in q.all()]

    @classmethod
    def get_multi(cls, name, start=0, limit=20):
        '''按照名字取应用列表, 从start开始取limit个'''
        q = db.session.query(cls).filter(cls.name == name).order_by(cls.id.desc()).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    @classmethod
    def get(cls, id):
        return db.session.query(cls).filter(cls.id == id).first()

    def get_yaml(self, kind):
        key = '/NBE/{self.name}/{self.version}/{kind}'.format(self=self, kind=kind)
        r = etcd.get(key)
        return r.value if (r and not r.dir) else ''

    @cached_property
    def app_yaml(self):
        return self.get_yaml('app.yaml')

    @cached_property
    def config_yaml(self):
        return self.get_yaml('config.yaml')

    @cached_property
    def test_yaml(self):
        return self.get_yaml('test.yaml')

    @cached_property
    def original_config_yaml(self):
        return self.get_yaml('original-config.yaml')

    @cached_property
    def containers(self):
        '''应用的所有container'''
        from .container import Container
        return Container.get_multi(app_id=self.id)

    @cached_property
    def n_container(self):
        '''container数量'''
        return len(self.containers)

    @cached_property
    def hosts(self):
        '''这个应用所处的host'''
        from .host import Host
        host_ids = list(set(c.host_id for c in self.containers))
        return filter(None, [Host.get(i) for i in host_ids])

    @property
    def gitlab_id(self):
        return quote('%s/%s' % (self.group, self.name), safe='')

    def is_daemon(self):
        y = yaml_loads(self.app_yaml)
        return y.get('daemon', False)

    def tasks(self, status=None, succ=None, start=0, limit=20):
        from .task import StoredTask
        return StoredTask.get_multi(self.id, status, succ)

    def processing_tasks(self, start=0, limit=20):
        return self.tasks(status=TaskStatus.Running, start=start, limit=limit)

    def processing(self):
        return len(self.processing_tasks(limit=1)) > 0

    def git_repo_url(self):
        return 'http://git.hunantv.com/{self.group}/{self.pname}'.format(self=self)

    def online_url(self):
        return 'http://{self.name}.intra.hunantv.com'.format(self=self)

    def realtime_metric_data(self, metric='cpu_usage', time='10s', limit=100):
        try:
            sql = ("select sum(value) from %s where "
                   "metric='%s' group by time(%s) limit %s" % (self.name, metric, time, limit))
            return influxdb.query(sql)[0]
        except:
            return {'data': [], 'name': ''}
