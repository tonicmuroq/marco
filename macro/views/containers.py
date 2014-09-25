# coding: utf-8

import os
import yaml
from flask import Blueprint, jsonify

from macro.ext import etcd
from macro.utils import yaml_loads


bp = Blueprint('container', __name__, url_prefix='/container')


@bp.route('/<app>/hosts')
def index(app):
    key = os.path.join(os.environ['ETCD_PREFIX'], app, 'apps')
    r = etcd.get(key)
    hosts = [c.key.rsplit('/', 1)[-1] for c in r.children]
    return jsonify({'r': 0, 'hosts': hosts})


@bp.route('/<app>/<host>/containers')
def containers(app, host):
    key = os.path.join(os.environ['ETCD_PREFIX'], app, 'apps', host)
    r = etcd.get(key)
    containers = [yaml_loads(c.value) for c in r.children]
    return jsonify({'r': 0, 'containers': containers})
