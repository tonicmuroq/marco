# coding: utf-8

from flask.ext.sqlalchemy import SQLAlchemy
from .openid2_ext import OpenID2
from .etcd_ext import Etcd
from .elasticsearch_ext import ElasticSearch
from .influxdb_ext import InfluxDB

db = SQLAlchemy()
etcd = Etcd()
es = ElasticSearch()
influxdb = InfluxDB()
openid2 = OpenID2()

__all__ = ['db', 'etcd', 'es', 'influxdb', 'openid2',
        'SQLAlchemy', 'Etcd', 'ElasticSearch', 'InfluxDB', 'OpenID2']
