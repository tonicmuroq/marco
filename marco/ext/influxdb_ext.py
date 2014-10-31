# coding: utf-8

from urlparse import urlparse
from influxdb import InfluxDBClient
from flask import current_app, _app_ctx_stack

class InfluxDB(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('INFLUXDB_URI', 'http://localhost:8086')

    def connect(self):
        es_uri = current_app.config['INFLUXDB_URI']
        parsed = urlparse(es_uri)
        return InfluxDBClient(host=parsed.hostname, port=parsed.port,
                username=parsed.username, password=parsed.password,
                database=parsed.path[1:])

    @property
    def influxdb(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'influxdb'):
                ctx.influxdb = self.connect()
            return ctx.influxdb

    def __getattr__(self, name):
        return getattr(self.influxdb, name)
