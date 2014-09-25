# coding: utf-8

import yaml
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def yaml_loads(s):
    return yaml.load(StringIO(s))
