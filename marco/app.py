# coding: utf-8

import os
import yaml

from flask import Flask
from werkzeug.utils import import_string

from marco.ext import db, etcd
from marco.views.navigator import init_nav


blueprints = (
    'index',
    'containers',
    'application',
)


def load_config():
    config = {}
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.load(f)
    return config


def create_app():
    app = Flask(__name__, static_url_path='/marco/static')
    app.config.update(load_config())

    db.init_app(app)
    etcd.init_app(app)
    init_nav(app)

    for bp in blueprints:
        import_name = '%s.views.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    return app
