# coding: utf-8

import json
from flask import Blueprint, Response, g


bp = Blueprint('env', __name__, url_prefix='/env')


@bp.route('/dot', methods=['POST', ])
def set_dot_env():
    env = g.dot_env == 'intra' and 'online' or 'intra'
    resp = Response(json.dumps({'r': 0, 'env': env}), mimetype='application/json')
    resp.set_cookie('dotenv', env)
    return resp
