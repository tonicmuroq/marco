# coding: utf-8

from flask import Blueprint, render_template, abort, request

from marco.models.host import Host
from marco.models.container import Container


bp = Blueprint('host', __name__, url_prefix='/host')


@bp.route('/')
def index():
    hosts = Host.all_hosts()
    return render_template('/host/index.html', hosts=hosts)


@bp.route('/<host_id>/')
def host_info(host_id):
    host = Host.get(host_id)
    if not host:
        abort(404)
    cs = Container.get_multi(host.id)
    return render_template('/host/host.html', containers=cs, host=host)
