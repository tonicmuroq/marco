# coding: utf-8

from werkzeug import cached_property

from marco.ext import db, etcd
from .base import Base


class Container(Base):

    __tablename__ = 'container'

    container_id = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, default=0)
    host_id = db.Column(db.Integer, default=0)
    app_id = db.Column(db.Integer, default=0)
    daemon_id = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_by_container_id(cls, cid):
        return db.session.query(cls).filter(cls.container_id.like('%s%%' % cid)).first()

    @classmethod
    def get_multi(cls, host_id, app_id=None):
        q = db.session.query(cls).filter(cls.host_id == host_id)
        if app_id is not None:
            q = q.filter(cls.app_id == app_id)
        return q.order_by(cls.app_id.asc()).all()

    @cached_property
    def application(self):
        from .application import Application
        return Application.get(self.app_id)
