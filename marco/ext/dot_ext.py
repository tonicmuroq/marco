# coding: utf-8

from urlparse import urlparse
from flask import current_app, g, _app_ctx_stack

from marco.dot import DotClient

class Dot(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('DOT_URL', 'http://localhost:5000')

    def connect(self, env):
        dot_uri = current_app.config['DOT_URL_%s' % env.upper()]
        parsed = urlparse(dot_uri)
        return DotClient(host=parsed.hostname, port=parsed.port, scheme=parsed.scheme)

    def dot(self, env):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if env == 'online':
                if not hasattr(ctx, 'dot_online'):
                    ctx.dot_online = self.connect(env)
                return ctx.dot_online
            if env == 'intra':
                if not hasattr(ctx, 'dot_intra'):
                    ctx.dot_intra = self.connect(env)
                return ctx.dot_intra

    def __getattr__(self, name):
        dot = self.dot(g.dot_env)
        return getattr(dot, name)
