# coding: utf-8

import random
from flask import Blueprint, request, g

from marco.ext import dot, gitlab
from marco.models.host import Host, Core
from marco.models.pod import UserPod
from marco.models.container import Container
from marco.models.application import AppVersion, Application

from marco.views.utils import jsonify


bp = Blueprint('ajax', __name__, url_prefix='/ajax')


class AppNotReadyError(Exception):
    message = 'App not ready yet'


class AppNotFoundError(Exception):
    message = 'App not found'


def _get_app(id, validate_process=False):
    app = AppVersion.get(id)
    if not app:
        raise AppNotFoundError()
    if validate_process and app.processing():
        raise AppNotReadyError()
    return app


@bp.route('/app/<name>/update', methods=['POST', ])
@jsonify
def update_app(name):
    to_version = request.form['to_version']
    cs = Container.get_multi_by_app_name(name)
    update_args = {}
    for c in cs:
        update_args.setdefault(c.appversion.version, []).append(c.host.ip)
    for version, hosts in update_args.iteritems():
        if version == to_version:
            continue
        hosts = list(set(hosts))
        dot.update_app(name, version, to_version, hosts)
    return {'r': 0}


@bp.route('/app/<appname>/all_metrics')
@jsonify
def app_all_metric(appname):
    app = Application.get_by_name(appname)
    data = app.all_realtime_metric_data(
        request.args.get('time', type=int, default=10), request.args.get('limit', type=int, default=100))
    return {k: v.get('points', []) for k, v in data.iteritems()}


@bp.route('/app/<app_id>/add', methods=['POST', ])
@jsonify
@Core.try_bind_container
def app_add_container(app_id):
    daemon = request.form.get('daemon', 'false')
    sub_app = request.form.get('sub_app', '')
    app = _get_app(app_id, validate_process=False)

    if not request.form.get('retain'):
        host = random.choice(Host.all_hosts())
        return dot.add_container(app, host, daemon, sub_app)

    try:
        core_count = int(request.form['cores'])
        container_count = int(request.form['containers'])
    except ValueError, e:
        return 'invalid argument (%s)' % e.message, 400

    user_pod = UserPod.get_by_user_pod(g.user.id, g.pod.id)
    if (user_pod is None or user_pod.core_quota - user_pod.core_quota_used
            < core_count * container_count):
        return 'insufficient core quota', 400

    hosts = sorted(Host.all_hosts(), key=lambda h: len(h.free_cores))
    container_hosts = []
    cores = []
    for h in hosts:
        n = min(len(h.free_cores) / core_count,
                container_count - len(container_hosts))
        cores.extend(h.free_cores[:n * core_count])
        container_hosts.extend(
            [(h, h.free_cores[i * core_count: (i + 1) * core_count])
             for i in xrange(n)])
        if len(container_hosts) == container_count:
            break

    exc_uuid = Core.occupy_cores(cores, g.user.id)
    for h, cores in container_hosts:
        task_id = dot.add_container(app, h, daemon, sub_app,
                                    [c.cpu_id for c in cores])
        Core.bind_to_task(cores, task_id)
    return ''


@bp.route('/app/<app_id>/build', methods=['POST', ])
@jsonify
def app_build_image(app_id):
    _runtime = {
        'python': 'docker-registry.intra.hunantv.com/nbeimage/ubuntu:python-2014.11.28',
        'java': 'docker-registry.intra.hunantv.com/nbeimage/ubuntu:java-2014.11.28',
        'nodejs': 'docker-registry.intra.hunantv.com/nbeimage/ubuntu:nodejs-2014.12.1',
        'php': 'docker-registry.intra.hunantv.com/nbeimage/ubuntu:php-2014.12.18',
    }
    base = request.form['base']
    host = Host.get(request.form['host_id'])
    if not host:
        return {'r': 1, 'msg': 'no such host'}

    app = _get_app(app_id, validate_process=True)
    if base == 'auto':
        base = _runtime.get(app.runtime, '')
    return dot.build_image(app, host, base)


@bp.route('/app/<app_id>/test', methods=['POST', ])
@jsonify
def app_test_app(app_id):
    host = Host.get(request.form['host_id'])
    if not host:
        return {'r': 1, 'msg': 'no such host'}

    app = _get_app(app_id, validate_process=True)
    return dot.test_app(app, host)


@bp.route('/app/<app_id>/remove', methods=['POST', ])
@jsonify
def app_remove_app(app_id):
    host = Host.get(request.form['host_id'])
    if not host:
        return {'r': 1, 'msg': 'no such host'}

    app = _get_app(app_id, validate_process=True)
    if app.name in ('marco', 'openids'):
        return {'r': 1, 'msg': '不允许下线这些'}
    return dot.remove_app(app, host)


@bp.route('/app/<app_id>/syncdb', methods=['POST', ])
@jsonify
def app_sync_db(app_id):
    app = _get_app(app_id)
    schema = app.app_yaml.get('schema', '')
    if schema:
        sql = gitlab.getrawblob(app.gitlab_id, app.version, schema)
        return dot.syncdb(app.name, sql)
    return {'r': 0}


@bp.route('/container/remove', methods=['POST', ])
@jsonify
@Core.try_bind_container
def remove_containers():

    def _filter_container(c):
        if not c:
            return False
        # XD
        if g.user.username == 'tonic':
            return True
        return c.application.name not in ('marco', 'openids')

    cids = request.form.getlist('cids[]')
    cs = [Container.get_by_container_id(cid) for cid in cids if cid]
    for c in filter(_filter_container, cs):
        dot.remove_container(c)
        Core.retire_cores_in_container(c.container_id)
    return {'r': 0, 'msg': 'ok'}


@bp.errorhandler(AppNotReadyError)
@bp.errorhandler(AppNotFoundError)
@jsonify
def error_handler(error):
    return {'r': 1, 'msg': error.message}


@bp.before_request
@jsonify
def test_if_logged_in():
    if not g.user:
        return {'r': 1, 'msg': 'need login'}
