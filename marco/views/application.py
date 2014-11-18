# coding: utf-8
from flask import (Blueprint, request, render_template,
        abort, g, redirect, url_for)

from marco.ext import openid2, dot
from marco.models.application import Application, get_config_yaml


bp = Blueprint('app', __name__, url_prefix='/app')


def _get_app(name, version):
    app = Application.get_by_name_and_version(name, version)
    if not app:
        abort(404)
    return app


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


@bp.route('/<appname>/settings/', methods=['POST', 'GET', ])
def settings(appname):
    if request.method == 'POST':
        branch = request.form.get('branch', type=str)
        dot.set_hook_branch(appname, branch)

    hook_branch = dot.get_hook_branch(appname)
    config = get_config_yaml(appname, 'prod')
    return render_template('/app/app_settings.html',
            appname=appname, hook_branch=hook_branch, config=config)


@bp.route('/<appname>/settings/resources', methods=['POST'])
def add_resource(appname):
    resource = request.form.get('resource', type=str)
    name = request.form.get('name', type=str)
    env = request.form.get('env', type=str)
    dot.add_resource(appname, resource, name, env)
    return redirect(url_for('app.settings', appname=appname))


@bp.route('/<name>/<version>/')
def single_version(name, version):
    app = _get_app(name, version)
    ptasks = app.processing_tasks(limit=5)
    tasks = app.tasks(limit=10)
    return render_template('/app/app.html', app=app, ptasks=ptasks, tasks=tasks)


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
