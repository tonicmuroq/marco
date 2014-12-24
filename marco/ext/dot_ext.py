# coding: utf-8

from urlparse import urlparse
from flask import g, _app_ctx_stack

from marco.dot import DotClient

class Dot(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('DOT_URL', 'http://localhost:5000')

    def connect(self, url):
        parsed = urlparse(url)
        return DotClient(host=parsed.hostname, port=parsed.port, scheme=parsed.scheme)

    def dot(self, pod):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            name = 'dot_%s' % pod.name
            if not hasattr(ctx, name):
                setattr(ctx, name, self.connect(pod.dot_url))
            return getattr(ctx, name)

    def __getattr__(self, name):
        dot = self.dot(g.pod)
        return getattr(dot, name)
