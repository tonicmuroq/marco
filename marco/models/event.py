# coding: utf-8

import json
from datetime import datetime

from marco.ext import db
from marco.models.base import Base


class Event(Base):

    __bind_key__ = 'marco'
    __tablename__ = 'event'
    __table_args__ = (
        db.Index('user_type_time', 'user_id', 'type', 'time'),
        db.Index('user_time', 'user_id', 'time'),
    )

    user_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.Integer, default=0, index=True)
    properties = db.Column(db.String(255))

    @classmethod
    def get_multi_by_user(cls, user_id, type=None, start=0, limit=20):
        q = db.query(cls).filter(cls.user_id == user_id)
        if type is not None:
            q = q.filter(cls.type == type)
        q = q.order_by(cls.time.desc()).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    @classmethod
    def create(cls, user_id, type, props):
        e = cls(user_id=user_id, type=type, properties=json.dumps(props))
        db.session.add(e)
        db.session.commit()
        return e

    @property
    def props(self):
        return json.loads(self.properties)

    def update_props(self, **kw):
        p = self.props.update(**kw)
        self.properties = json.dumps(p)
        db.session.add(self)
        db.session.commit()
