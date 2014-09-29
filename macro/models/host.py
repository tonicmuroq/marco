# coding: utf-8

from macro.ext import db
from .base import Base


class Host(Base):

    __tablename__ = 'host'

    ip = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))

    @classmethod
    def get_by_ip(cls, ip):
        return db.session.query(cls).filter(cls.ip == ip).first()

    @classmethod
    def get(cls, id):
        return db.session.query(cls).filter(cls.id == id).first()

    @classmethod
    def all_hosts(cls):
        return db.session.query(cls).order_by(cls.id).all()
