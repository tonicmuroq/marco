# coding: utf-8

import os
import yaml
import logging

from flask import Flask
from werkzeug.utils import import_string

from marco.ext import db, etcd, es, influxdb, openid2
from marco.views.navigator import init_nav

blueprints = (
    'ajax',
    'index',
    'host',
    'hook',
    'task',
    'container',
    'application',
)


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.load(f)


def create_app():
    config = load_config()

    app = Flask(__name__, static_url_path='/marco/static')
    app.config.update(config)

    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO if os.getenv('NBE_RUNENV')
                        else logging.DEBUG)

    db.init_app(app)
    etcd.init_app(app)
    es.init_app(app)
    influxdb.init_app(app)
    openid2.init_app(app)
    init_nav(app)

    for bp in blueprints:
        import_name = '%s.views.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    return app
