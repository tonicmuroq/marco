# coding: utf-8

from sqlalchemy import distinct
from werkzeug import cached_property

from marco.ext import db, etcd
from .base import Base


class Application(Base):

    __tablename__ = 'application'

    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    pname = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_by_name_and_version(cls, name, version):
        return db.session.query(cls).filter(cls.name == name, cls.version == version).first()

    @classmethod
    def get_all_app_names(cls, limit=None):
        q = db.session.query(cls.name).distinct(cls.name).order_by(cls.name.asc())
        if limit is not None:
            q = q.limit(limit)
        return [r for r, in q.all()]

    @classmethod
    def get_multi(cls, name, limit=None):
        q = db.session.query(cls).filter(cls.name == name).order_by(cls.name.asc())
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
    def n_container(self):
        from .container import Container
        return len(Container.get_multi(app_id=self.id))

    @cached_property
    def containers(self):
        from .container import Container
        return Container.get_multi(app_id=self.id)
