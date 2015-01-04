# coding: utf-8

from urlparse import urlparse
from influxdb import InfluxDBClient
from flask import _app_ctx_stack, g

class InfluxDB(object):

    def connect(self, url):
        parsed = urlparse(url)
        return InfluxDBClient(host=parsed.hostname, port=parsed.port,
                username=parsed.username, password=parsed.password,
                database=parsed.path[1:])

    def influxdb(self, pod):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            name = 'influxdb_%s' % pod.name
            if not hasattr(ctx, name):
                setattr(ctx, name, self.connect(pod.influxdb))
            return getattr(ctx, name)

    def __getattr__(self, name):
        influxdb = self.influxdb(g.pod)
        return getattr(influxdb, name)
