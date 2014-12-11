# coding: utf-8
import json
from flask import (Blueprint, Response, request, render_template,
        abort, g, redirect, url_for)

from marco.ext import openid2, dot
from marco.models.host import Host
from marco.models.application import Application, AppVersion, get_config_yaml


bp = Blueprint('app', __name__, url_prefix='/app')


def _get_appversion(name, version):
    app = AppVersion.get_by_name_and_version(name, version)
    if not app:
        abort(404)
    return app


@bp.route('/')
def index():
    app_names = Application.get_all_app_names(limit=20)
    return render_template('/app/index.html', app_names=app_names)


@bp.route('/<name>/jobs')
def job_history(name):
    app = Application.get_by_name(name)
    tasks = app.tasks()
    return render_template('/app/jobs.html', tasks=tasks, app=app)


@bp.route('/<name>/metrics')
def metrics(name):
    app = Application.get_by_name(name)
    return render_template('/app/metrics.html', app=app)


@bp.route('/<name>/collect', methods=['POST', ])
def collect(name):
    if name in g.collected_apps:
        g.collected_apps = [n for n in g.collected_apps if n != name]
        action = 'remove'
    else:
        g.collected_apps.append(name)
        action = 'add'
    resp = Response(json.dumps({'r': 0, 'action': action}), mimetype='application/json')
    resp.set_cookie('collected_apps', ','.join(g.collected_apps))
    return resp


@bp.route('/<name>/')
def app_set_info(name):
    app = Application.get_by_name(name)
    if not app:
        abort(404)
    apps = app.all_versions()
    online_apps = [a for a in apps if a.n_container]
    return render_template('/app/versions.html', apps=apps,
            latest=apps[0], online_apps=online_apps, app=app)


@bp.route('/<name>/settings/', methods=['POST', 'GET', ])
def settings(name):
    app = Application.get_by_name(name)
    if request.method == 'POST':
        branch = request.form.get('branch', type=str)
        dot.set_hook_branch(app.name, branch)

    hook_branch = dot.get_hook_branch(app.name)
    config = get_config_yaml(app.name, 'prod')
    return render_template('/app/settings.html',
            hook_branch=hook_branch, config=config, app=app)


@bp.route('/<name>/settings/resources', methods=['POST'])
def add_resource(name):
    app = Application.get_by_name(name)
    resource = request.form.get('resource', type=str)
    name = request.form.get('name', type=str)
    env = request.form.get('env', type=str)
    dot.add_resource(app.name, resource, name, env)
    return redirect(url_for('app.settings', app=app))


@bp.route('/<name>/<version>/')
def app_version(name, version):
    app = _get_appversion(name, version)
    ptasks = app.processing_tasks(limit=5)
    tasks = app.tasks(limit=10)
    hosts = Host.all_hosts()
    return render_template('/app/appversion.html', app=app,
            ptasks=ptasks, tasks=tasks, hosts=hosts)


@bp.route('/<name>/<version>/jobs')
def av_job_history(name, version):
    app = _get_appversion(name, version)
    tasks = app.tasks(limit=10)
    return render_template('/app/av_jobs.html', app=app, tasks=tasks)


@bp.route('/<name>/<version>/av')
def single_version(name, version):
    app = _get_appversion(name, version)
    ptasks = app.processing_tasks(limit=5)
    tasks = app.tasks(limit=10)
    hosts = Host.all_hosts()
    return render_template('/app/app.html', app=app,
            ptasks=ptasks, tasks=tasks, hosts=hosts)


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
