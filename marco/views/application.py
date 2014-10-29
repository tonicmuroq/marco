# coding: utf-8
import gitlab
from flask import Blueprint, request, render_template, abort, current_app

from marco.actions import (add_container, build_image, test_app,
        remove_app, sync_database as syncdb, update_app_to_version)
from marco.models.application import Application
from marco.models.container import Container
from marco.models.host import Host

from marco.utils import yaml_loads
from marco.views.utils import jsonify


bp = Blueprint('app', __name__, url_prefix='/app')


class AppNotReadyError(Exception):
    message = 'App not ready yet'


class AppNotFoundError(Exception):
    message = 'App not found'


@bp.route('/')
def index():
    app_names = Application.get_all_app_names(limit=20)
    return render_template('/app/index.html', app_names=app_names)


@bp.route('/<name>/')
def app_set_info(name):
    apps = Application.get_multi(name)
    if not apps:
        abort(404)
    latest = apps[0]
    online_apps = [a for a in apps if a.n_container]
    return render_template('/app/app_set.html', apps=apps,
            latest=latest, online_apps=online_apps)


@bp.route('/<name>/update', methods=['POST', ])
@jsonify
def update_app(name):
    to_version = request.form['to_version']
    cs = Container.get_multi_by_app_name(name)
    update_args = {}
    for c in cs:
        update_args.setdefault(c.application.version, []).append(c.host.ip)
    for version, hosts in update_args.iteritems():
        if version == to_version:
            continue
        hosts = list(set(hosts))
        update_app_to_version(name, version, to_version, hosts)
    return {'r': 0}


@bp.route('/<name>/<version>/')
def app_info(name, version):
    app = Application.get_by_name_and_version(name, version)
    ptasks = app.processing_tasks(limit=5)
    tasks = app.tasks(limit=10)
    if not app:
        abort(404)
    return render_template('/app/app.html', app=app, ptasks=ptasks, tasks=tasks)


@bp.route('/<name>/<version>/metrics')
@jsonify
def app_metric(name, version):
    app = Application.get_by_name_and_version(name, version)
    metric_name = request.args.get('metric_name', 'cpu_usage')
    data = app.realtime_metric_data(metric_name)
    points = [{'series': 0, 'x': p[0], 'y': p[1]} for p in data.get('points', [])]
    return {"data": [{'key': data['name'], 'values': points}, ]}


@bp.route('/<name>/<version>/tasks')
def app_tasks(name, version):
    app = Application.get_by_name_and_version(name, version)
    if not app:
        abort(404)
    tasks = app.tasks()
    return render_template('/app/app_task.html', app=app, tasks=tasks)


@bp.route('/<name>/<version>/add', methods=['POST'])
@jsonify
def app_add_container(name, version):
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    validate_app(app)
    return add_container(app, host)


@bp.route('/<name>/<version>/build', methods=['POST'])
@jsonify
def app_build_image(name, version):
    base = request.form['base']
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    validate_app(app)
    return build_image(app, host, base)


@bp.route('/<name>/<version>/test', methods=['POST'])
@jsonify
def app_test_app(name, version):
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    validate_app(app)
    return test_app(app, host)


@bp.route('/<name>/<version>/remove', methods=['POST'])
@jsonify
def app_remove_app(name, version):
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    if app.name == 'marco':
        return jsonify({"r": 1, "msg": "marco 不能下光!"})
    validate_app(app)
    return remove_app(app, host)


@bp.route('/<name>/<version>/syncdb', methods=['POST', ])
@jsonify
def sync_database(name, version):
    app = Application.get_by_name_and_version(name, version)
    if not app:
        raise AppNotFoundError()
    git = gitlab.Gitlab(current_app.config['GITLAB_URL'],
            token=current_app.config['GITLAB_TOKEN'])
    y = yaml_loads(app.app_yaml)
    schema = y.get('schema', '')
    if schema:
        sql = git.getrawblob(app.gitlab_id, app.version, schema)
        return syncdb(app, sql)
    return {'r': 0}


def validate_app(app):
    if not app:
        raise AppNotFoundError()
    if app.processing():
        raise AppNotReadyError()


@bp.errorhandler(AppNotReadyError)
@bp.errorhandler(AppNotFoundError)
@jsonify
def error_handler(error):
    return {"r": 1, "msg": error.message}
