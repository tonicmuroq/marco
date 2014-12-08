# coding: utf-8

from werkzeug import cached_property

from marco.ext import db
from .base import Base


class Host(Base):

    __tablename__ = 'host'

    ip = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    status = db.Column(db.Integer)

    @classmethod
    def get_by_ip(cls, ip):
        return db.session.query(cls).filter(cls.ip == ip).one()

    @classmethod
    def get(cls, id):
        return db.session.query(cls).filter(cls.id == id).one()

    @classmethod
    def all_hosts(cls, start=0, limit=20):
        q = db.session.query(cls).order_by(cls.id).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def is_online(self):
        return self.status == 0

    @cached_property
    def containers(self):
        from .container import Container
        return Container.get_multi(host_id=self.id)

    @cached_property
    def apps(self):
        from .application import Application
        app_ids = list(set(c.app_id for c in self.containers))
        return filter(None, [Application.get(i) for i in app_ids])
