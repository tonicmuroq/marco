# coding: utf-8

from urlparse import urlparse
import etcd as petcd
from elasticsearch import Elasticsearch
from influxdb import InfluxDBClient

from flask import current_app, _app_ctx_stack
from flask.ext.sqlalchemy import SQLAlchemy


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
        return petcd.Client(host=parsed.hostname, port=parsed.port)

    @property
    def etcd(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'etcd'):
                ctx.etcd = self.connect()
            return ctx.etcd

    def __getattr__(self, name):
        return getattr(self.etcd, name)


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


db = SQLAlchemy()
etcd = Etcd()
es = ElasticSearch()
influxdb = InfluxDB()
