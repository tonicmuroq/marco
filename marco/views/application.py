# coding: utf-8
import gitlab
from flask import (Blueprint, request, render_template,
        abort, current_app, g, redirect)

from marco.ext import openid2
from marco.actions import (add_container, build_image, test_app,
        remove_app, sync_database as syncdb, update_app_to_version,
        add_mysql, set_hook_branch, get_hook_branch)
from marco.models.application import Application
from marco.models.container import Container
from marco.models.host import Host

from marco.utils import yaml_loads
from marco.views.utils import jsonify


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


@bp.route('/<name>/<version>/resources')
def app_resource(name, version):
    app = _get_app(name, version)
    config = yaml_loads(app.config_yaml)
    mysqls = {k: v for k, v in config.iteritems() if k.startswith('mysql')}
    redises = {k: v for k, v in config.iteritems() if k.startswith('redis')}
    return render_template('/app/app_resource.html',
            app=app, config=config, mysqls=mysqls, redises=redises)


@bp.route('/<name>/settings/', methods=['POST', 'GET', ])
def app_settings(name):
    if request.method == 'POST':
        branch = request.form.get('branch', type=str)
        set_hook_branch(name, branch)

    hook_branch = get_hook_branch(name)
    return render_template('/app/app_settings.html',
            name=name, hook_branch=hook_branch)


@bp.route('/<name>/<version>/')
def app_info(name, version):
    app = _get_app(name, version)
    ptasks = app.processing_tasks(limit=5)
    tasks = app.tasks(limit=10)
    return render_template('/app/app.html', app=app, ptasks=ptasks, tasks=tasks)


@bp.route('/<name>/<version>/tasks')
def app_tasks(name, version):
    app = _get_app(name, version)
    tasks = app.tasks()
    return render_template('/app/app_task.html', app=app, tasks=tasks)


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
