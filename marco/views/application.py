# coding: utf-8

import re
import json
import yaml
from flask import (Blueprint, Response, request, render_template,
        abort, g, redirect, url_for, jsonify)

from marco.ext import openid2, dot
from marco.models.host import Host
from marco.models.application import Application, AppVersion, get_config_yaml, set_config_yaml


bp = Blueprint('app', __name__, url_prefix='/app')


def _get_appversion(name, version):
    app = AppVersion.get_by_name_and_version(name, version)
    if not app:
        abort(404)
    return app


@bp.route('/')
def index():
    return redirect(url_for('index.index'))


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
    config = get_config_yaml(app.name, 'prod')
    storage = {k: config.get(k, None) for k in ('mysql', 'redis')}
    sentry = config.get('sentry_dsn', '')
    influxdb = config.get('influxdb', {})
    zipkin = config.get('zipkin', False)
    return render_template('/app/settings.html', config=config,
            storage=storage, sentry=sentry, influxdb=influxdb, zipkin=zipkin,
            app=app)


@bp.route('/<name>/settings/resources', methods=['POST'])
def add_resource(name):
    app = Application.get_by_name(name)
    resource = request.form.get('resource', type=str)
    name = request.form.get('name', type=str)
    env = request.form.get('env', type=str)
    dot.add_resource(app.name, resource, name, env)
    return redirect(url_for('app.settings', name=app.name))


@bp.route('/<name>/settings/sentry', methods=['POST'])
def add_sentry(name):
    app = Application.get_by_name(name)
    av = app.all_versions()[0]
    dot.add_sentry(name, av.runtime)
    return redirect(url_for('app.settings', name=app.name))


@bp.route('/<name>/settings/influxdb', methods=['POST'])
def add_influxdb(name):
    dot.add_influxdb(name)
    return redirect(url_for('app.settings', name=name))


@bp.route('/<name>/settings/zipkin', methods=['POST'])
def use_zipkin(name):
    config = get_config_yaml(name, 'prod')
    value = request.form.get('zipkin', 'off')
    config['zipkin'] = True if value == 'on' else False
    r = set_config_yaml(name, 'prod', config)
    return jsonify({'r': r})


@bp.route('/<name>/<version>/')
def app_version(name, version):
    app = _get_appversion(name, version)
    ptasks = app.processing_tasks(limit=5)
    tasks = app.tasks(limit=10)
    hosts = Host.all_hosts()
    return render_template(
        '/app/appversion.html', app=app, ptasks=ptasks, tasks=tasks,
        hosts=hosts, sub_apps=dot.get_sub_appyamls(app))


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

_SUB_NAME_CHECK = re.compile('^[a-zA-Z]+$')


@bp.route('/<name>/<version>/addsub', methods=['POST'])
def add_sub_app(name, version):
    def split_lines(val):
        return filter(None, [ln.strip() for ln in val.split('\n')])

    app = _get_appversion(name, version)
    subname = request.form['subname']
    if not _SUB_NAME_CHECK.match(subname):
        return 'invalid sub name', 400
    dot.add_sub_appyaml(app, yaml.safe_dump({
        'appname': app.name + '-' + subname,
        'port': int(request.form['port']),
        'runtime': request.form['runtime'],
        'build': split_lines(request.form['build']),
        'cmd': split_lines(request.form['cmd']),
        'daemon': split_lines(request.form['daemon']),
        'static': request.form['static'],
    }, default_flow_style=False))
    return ''


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
