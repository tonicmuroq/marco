# coding: utf-8

import os
from flask import (Blueprint, jsonify, current_app,
        request, render_template, redirect, url_for)

from marco.ext import etcd
from marco.models import Container
from marco.utils import yaml_loads
from marco.actions import remove_container


bp = Blueprint('container', __name__, url_prefix='/container')


@bp.route('/<app>/hosts')
def index(app):
    key = os.path.join(current_app.config['ETCD_PREFIX'], app, 'apps')
    r = etcd.get(key)
    hosts = [c.key.rsplit('/', 1)[-1] for c in r.children]
    return jsonify({'r': 0, 'hosts': hosts})


@bp.route('/<app>/<host>/containers')
def containers(app, host):
    key = os.path.join(current_app.config['ETCD_PREFIX'], app, 'apps', host)
    r = etcd.get(key)
    containers = [yaml_loads(c.value) for c in r.children]
    return jsonify({'r': 0, 'containers': containers})


@bp.route('/<cid>', methods=['GET', 'POST'])
def container(cid):
    c = Container.get_by_container_id(cid)
    app = c and c.application or None
    host = c and c.host or None
    if not (c and app and host):
        abort(404)
    if request.method == 'GET':
        return render_template('/container/container.html',
                container=c, app=app, host=host)
    elif request.method == 'POST':
        remove_container(c)
        return redirect(url_for('app.app_info',
            name=app.name, version=app.version))


@bp.route('/remove', methods=['POST'])
def remove_containers():
    cids = request.form.getlist('cids[]')
    if not cids:
        return jsonify({"r": 1, "msg": "no containers"})
    cs = [Container.get_by_container_id(cid) for cid in cids]
    for c in filter(None, cs):
        remove_container(c)
    return jsonify({"r": 0, "msg": "ok"})
