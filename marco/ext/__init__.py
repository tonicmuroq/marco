# coding: utf-8

import os

from flask.ext.sqlalchemy import SQLAlchemy
from .openid2_ext import OpenID2
from .etcd_ext import Etcd
from .elasticsearch_ext import ElasticSearch
from .influxdb_ext import InfluxDB
from .dot_ext import DotClient


db = SQLAlchemy()
etcd = Etcd()
es = ElasticSearch()
influxdb = InfluxDB()
openid2 = OpenID2(file_store_path=os.getenv('NBE_PERMDIR', ''))
dot = DotClient()

__all__ = [
    'db', 'etcd', 'es', 'influxdb', 'openid2', 'dot',
    'SQLAlchemy', 'Etcd', 'ElasticSearch',
    'InfluxDB', 'OpenID2', 'DotClient'
]
