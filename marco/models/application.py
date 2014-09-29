# coding: utf-8

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
