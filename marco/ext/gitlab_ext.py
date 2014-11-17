# coding: utf-8

from flask import current_app, _app_ctx_stack

import gitlab

class Gitlab(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('GITLAB_URL', 'http://localhost:5000')
        app.config.setdefault('GITLAB_TOKEN', '')

    def connect(self):
        gitlab_url = current_app.config['GITLAB_URL']
        token = current_app.config['GITLAB_TOKEN']
        return gitlab.Gitlab(gitlab_url, token=token)

    @property
    def gitlab(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'gitlab'):
                ctx.gitlab = self.connect()
            return ctx.gitlab

    def __getattr__(self, name):
        return getattr(self.gitlab, name)
