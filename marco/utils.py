# coding: utf-8

import yaml
import json
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def yaml_loads(s):
    return yaml.load(StringIO(s))


def yaml_to_json(y):
    '''蛋疼...'''
    return json.dumps(yaml_loads(y))
