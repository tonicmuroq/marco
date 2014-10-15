# coding: utf-8

from marco.ext import db

from .base import Base


class StoredTask(Base):

    __tablename__ = 'stored_task'

    app_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    succ = db.Column(db.Integer, nullable=False)
    kind = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)

    @classmethod
    def get_multi(cls, app_id, status=None, succ=None, start=0, limit=20):
        q = db.session.query(cls).filter(cls.app_id == app_id)        
        if status is not None:
            q = q.filter(cls.status == status.value)
        if succ is not None:
            q = q.filter(cls.succ == succ.value)
        q = q.offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()
