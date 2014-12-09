# coding: utf-8

from werkzeug import cached_property

from marco.ext import db
from .base import Base


class Container(Base):

    __tablename__ = 'container'

    container_id = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, default=0)
    host_id = db.Column(db.Integer, default=0)
    ident_id = db.Column(db.String(255), nullable=False)
    app_name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_by_container_id(cls, cid):
        # this is important...
        if not cid:
            return None
        return db.session.query(cls).filter(cls.container_id.like('%s%%' % cid)).first()

    @classmethod
    def get_multi(cls, host_id=None, app_name=None, version=None):
        q = db.session.query(cls)
        if host_id is not None:
            q = q.filter(cls.host_id == host_id)
        if app_name is not None:
            q = q.filter(cls.app_name == app_name)
        if version is not None:
            q = q.filter(cls.version == version)
        return q.order_by(cls.app_name.asc()).all()

    @classmethod
    def get_multi_by_app_name(cls, app_name):
        return db.session.query(cls).filter(cls.app_name == app_name).all()

    @cached_property
    def application(self):
        from .application import Application
        return Application.get_by_name(self.app_name)

    @cached_property
    def appversion(self):
        from .application import AppVersion
        return AppVersion.get_by_name_and_version(self.app_name, self.version)

    @cached_property
    def host(self):
        from .host import Host
        return Host.get(self.host_id)
