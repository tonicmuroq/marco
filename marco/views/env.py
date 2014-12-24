# coding: utf-8

import json
from flask import Blueprint, Response, request, g

from marco.models.pod import Pod


bp = Blueprint('env', __name__, url_prefix='/env')


@bp.route('/pod', methods=['POST', ])
def set_pod_name():
    name = request.form.get('name', type=str, default='')
    pod = Pod.get_by_name(name)
    if pod and pod.dot_url:
        g.pod_name = pod.name
        g.pod = pod
    resp = Response(json.dumps({'r': 0, 'env': g.pod_name}), mimetype='application/json')
    resp.set_cookie('podname', g.pod_name)
    return resp
