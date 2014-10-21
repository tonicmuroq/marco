# coding: utf-8

import json
from functools import wraps

from flask import Response, g, request


def jsonify(f):
    @wraps(f)
    def _(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(json.dumps(r), mimetype='application/json')
    return _


def parse_start_and_limit(default_start=0, default_limit=20):
    g.start = request.args.get('start', default=default_start, type=int)
    g.limit = request.args.get('limit', default=default_limit, type=int)
