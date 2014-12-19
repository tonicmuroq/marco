# coding: utf-8

import os
import yaml
import logging

from flask import Flask, request, g
from werkzeug.utils import import_string

from marco.ext import etcd, es, influxdb, openid2, dot, gitlab
from marco.views.navigator import init_nav

blueprints = (
    'env',
    'ajax',
    'index',
    'host',
    'hook',
    'task',
    'container',
    'application',
    'manage',
)


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               'env.yaml')
    with open(config_path, 'r') as f:
        return yaml.load(f)


def create_app():
    config = load_config()

    app = Flask(__name__, static_url_path='/marco/static')
    app.config.update(config)
    app.secret_key = 'wolegeca'

    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO)

    etcd.init_app(app)
    es.init_app(app)
    influxdb.init_app(app)
    openid2.init_app(app)
    dot.init_app(app)
    gitlab.init_app(app)
    init_nav(app)

    for bp in blueprints:
        import_name = '%s.views.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    @app.before_request
    def init_global_vars():
        g.dot_env = request.cookies.get('dotenv', 'intra')

        collected_apps = request.cookies.get('collected_apps', None)
        g.collected_apps = collected_apps and collected_apps.split(',') or []

    return app
