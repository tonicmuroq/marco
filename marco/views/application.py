# coding: utf-8

from flask import Blueprint, request, render_template, abort

from marco.models.application import Application


bp = Blueprint('app', __name__, url_prefix='/app')


@bp.route('/')
def index():
    app_names = Application.get_all_app_names(limit=20)
    return render_template('/app/index.html', app_names=app_names)


@bp.route('/<name>/')
def app_set_info(name):
    apps = Application.get_multi(name)
    return render_template('/app/app_set.html', apps=apps)


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
