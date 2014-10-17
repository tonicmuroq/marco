# coding: utf-8

from flask import Blueprint, request, render_template, abort, jsonify

from marco.actions import add_container, build_image, test_app, remove_app
from marco.models.application import Application
from marco.models.host import Host


bp = Blueprint('app', __name__, url_prefix='/app')


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


@bp.route('/<name>/<version>/')
def app_info(name, version):
    app = Application.get_by_name_and_version(name, version)
    if not app:
        abort(404)
    return render_template('/app/app.html', app=app)


@bp.route('/<name>/<version>/tasks')
def app_tasks(name, version):
    app = Application.get_by_name_and_version(name, version)
    if not app:
        abort(404)
    tasks = app.tasks()
    return render_template('/app/app_task.html', app=app, tasks=tasks)


@bp.route('/<name>/<version>/add', methods=['POST'])
def app_add_container(name, version):
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    if not app:
        return jsonify({"r": 1, "msg": "no such app"})
    if app.is_doing_task():
        return jsonify({"r": 1, "msg": "正在执行其他任务"})
    r = add_container(app, host)
    return jsonify(r)


@bp.route('/<name>/<version>/build', methods=['POST'])
def app_build_image(name, version):
    base = request.form.get('base', 'http://docker-registry.intra.hunantv.com/nbeimage/ubuntu:python-2014.9.30')
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    if not app:
        return jsonify({"r": 1, "msg": "no such app"})
    if app.is_doing_task():
        return jsonify({"r": 1, "msg": "正在执行其他任务"})
    r = build_image(app, host, base)
    return jsonify(r)


@bp.route('/<name>/<version>/test', methods=['POST'])
def app_test_app(name, version):
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    if not app:
        return jsonify({"r": 1, "msg": "no such app"})
    if app.is_doing_task():
        return jsonify({"r": 1, "msg": "正在执行其他任务"})
    r = test_app(app, host)
    return jsonify(r)


@bp.route('/<name>/<version>/remove', methods=['POST'])
def app_remove_app(name, version):
    host_id = request.form['host_id']
    host = Host.get(host_id)
    if not host:
        return jsonify({"r": 1, "msg": "no such host"})

    app = Application.get_by_name_and_version(name, version)
    if not app:
        return jsonify({"r": 1, "msg": "no such app"})
    if app.name == 'marco':
        return jsonify({"r": 1, "msg": "marco 不能下光!"})
    if app.is_doing_task():
        return jsonify({"r": 1, "msg": "正在执行其他任务"})
    r = remove_app(app, host)
    return jsonify(r)
