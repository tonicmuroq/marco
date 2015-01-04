# coding: utf-8

from urlparse import urlparse
from elasticsearch import Elasticsearch
from flask import _app_ctx_stack, g 

class ElasticSearch(object):

    def connect(self, url):
        parsed = urlparse(url)
        return Elasticsearch(host=parsed.hostname, port=parsed.port)

    def es(self, pod):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            name = 'es_%s' % pod.name
            if not hasattr(ctx, name):
                setattr(ctx, name, self.connect(pod.es))
            return getattr(ctx, name)

    def __getattr__(self, name):
        es = self.es(g.pod)
        return getattr(es, name)
