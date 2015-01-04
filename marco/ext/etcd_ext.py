# coding: utf-8

import etcd
from urlparse import urlparse
from flask import _app_ctx_stack, g

class Etcd(object):

    def connect(self, url):
        parsed = urlparse(url)
        return etcd.Client(host=parsed.hostname, port=parsed.port)

    def etcd(self, pod):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            name = 'etcd_%s' % pod.name
            if not hasattr(ctx, name):
                setattr(ctx, name, self.connect(pod.etcd))
            return getattr(ctx, name)

    def __getattr__(self, name):
        etcd = self.etcd(g.pod)
        return getattr(etcd, name)
