# coding: utf-8

from urlparse import urlparse
from elasticsearch import Elasticsearch
from flask import current_app, _app_ctx_stack

class ElasticSearch(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('ES_URI', 'http://localhost:9200')

    def connect(self):
        es_uri = current_app.config['ES_URI']
        parsed = urlparse(es_uri)
        return Elasticsearch(host=parsed.hostname, port=parsed.port)

    @property
    def es(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'es'):
                ctx.es = self.connect()
            return ctx.es

    def __getattr__(self, name):
        return getattr(self.es, name)
