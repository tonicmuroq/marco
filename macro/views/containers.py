# coding: utf-8

import os
import yaml
from flask import Blueprint, jsonify, current_app

from macro.ext import etcd
from macro.models import Container
from macro.utils import yaml_loads


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


@bp.route('/<cid>')
def get_container(cid):
    c = Container.get_by_container_id(cid)
    return str(c)

@bp.route('/hosts')
def all_hosts():
    from macro.models.host import Host
    return str(Host.all_hosts())
