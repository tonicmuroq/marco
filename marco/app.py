# coding: utf-8

import os
import yaml
import json
import logging

from raven.contrib.flask import Sentry

from flask import Flask, request, g
from werkzeug.utils import import_string

from marco.ext import db, openid2, gitlab
from marco.models.pod import Pod, User

blueprints = (
    'env',
    'ajax',
    'index',
    'host',
    'host_adm',
    'hook',
    'task',
    'application',
    'manage',
    'pod',
)

template_filters = (
    enumerate,
)

DEV_MODE = os.getenv('NBE_RUNENV', 'DEV') == 'DEV'


def load_config(name):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), name)
    with open(config_path, 'r') as f:
        return yaml.load(f)


def _json_dump(o):
    def default(obj):
        from datetime import datetime
        if isinstance(obj, datetime):
            return long(1000 * calendar.timegm(obj.timetuple()))
        return obj
    return json.dumps(o, default=default).replace(
        '<', u'\\u003c').replace('>', u'\\u003e').replace(
            '&', u'\\u0026').replace("'", u'\\u0027')


def _join_textarea_content(ls):
    if ls is None:
        return ''
    return '\n'.join(ls)


def create_app():
    config = load_config('config.yaml')
    mysql_dsn = 'mysql://{username}:{password}@{host}:{port}/{db}'.format(**config['mysql'])
    sentry_dsn = config['sentry_dsn']

    app = Flask(__name__, static_url_path='/marco/static')
    app.config.update(load_config('env.yaml'))
    app.config.update(
        SQLALCHEMY_DATABASE_URI=mysql_dsn,
        SQLALCHEMY_POOL_SIZE=100,
        SQLALCHEMY_POOL_TIMEOUT=10,
        SQLALCHEMY_POOL_RECYCLE=3600,
    )
    app.secret_key = 'wolegeca'
    app.jinja_env.filters['tojson'] = _json_dump
    app.jinja_env.filters['join_textarea_content'] = _join_textarea_content

    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO)

    sentry = Sentry(dsn=sentry_dsn)
    if not DEV_MODE:
        sentry.init_app(app)

    for ext in (db, openid2, gitlab):
        ext.init_app(app)

    for ft in template_filters:
        app.add_template_global(ft)

    for bp in blueprints:
        import_name = '%s.views.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    @app.before_request
    def init_global_vars():
        g.pod_name = request.cookies.get('podname', 'intra')
        g.pod = Pod.get_by_name(g.pod_name)

        collected_apps = request.cookies.get('collected_apps', None)
        g.collected_apps = collected_apps and collected_apps.split(',') or []

        user_dict = json.loads(request.cookies.get(app.config['OPENID2_PROFILE_COOKIE_NAME'], '{}'))
        g.user = user_dict and User.get_or_create(user_dict['username'], user_dict['email']) or None

    return app
