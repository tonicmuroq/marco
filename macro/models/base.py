# coding: utf-8

from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import declared_attr

from macro.ext import db


class Base(db.Model):

    __abstract__ = True

    def __repr__(self):
        attrs = ('%s=%r' % (attr.key, attr.value) for attr in inspect(self).attrs)
        attrs_str = ', '.join(attrs)
        return '%s(%s)' % (self.__class__.__name__, attrs_str)

    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True)
