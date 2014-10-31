# coding: utf-8

import etcd
from urlparse import urlparse
from flask import current_app, _app_ctx_stack

class Etcd(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('ETCD_URI', 'http://localhost:4001')

    def connect(self):
        etcd_uri = current_app.config['ETCD_URI']
        parsed = urlparse(etcd_uri)
        return etcd.Client(host=parsed.hostname, port=parsed.port)

    @property
    def etcd(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'etcd'):
                ctx.etcd = self.connect()
            return ctx.etcd

    def __getattr__(self, name):
        return getattr(self.etcd, name)
