# coding: utf-8

from macro.ext import db, etcd
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
