# coding: utf-8

import os
import etcd as petcd

from flask import current_app, _app_ctx_stack
from flask.ext.sqlalchemy import SQLAlchemy


class Etcd(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('ETCD_URI', os.environ['ETCD_URI'])

    def connect(self):
        etcd_uri = current_app.config['ETCD_URI']
        host, port = etcd_uri.split(':')
        return petcd.Client(host=host, port=int(port))

    @property
    def etcd(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'etcd'):
                ctx.etcd = self.connect()
            return ctx.etcd

    def __getattr__(self, name):
        return getattr(self.etcd, name)


db = SQLAlchemy()
etcd = Etcd()
