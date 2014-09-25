# coding: utf-8

from flask import Flask
from werkzeug.utils import import_string


blueprints = (
    'containers',
)


def create_app():
    app = Flask(__name__)
    for bp in blueprints:
        import_name = '%s.views.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))
    return app
