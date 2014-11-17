# coding: utf-8

from urlparse import urlparse
from flask import current_app, _app_ctx_stack

from marco.dot import DotClient

class Dot(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('DOT_URL', 'http://localhost:5000')

    def connect(self):
        dot_uri = current_app.config['DOT_URL']
        parsed = urlparse(dot_uri)
        return DotClient(host=parsed.hostname, port=parsed.port, scheme=parsed.scheme)

    @property
    def dot(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'dot'):
                ctx.dot = self.connect()
            return ctx.dot

    def __getattr__(self, name):
        return getattr(self.dot, name)
