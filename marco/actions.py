# coding: utf-8

import requests
from urlparse import urljoin
from flask import current_app


API_FORMATS = {
    'add_container': '/app/{app.name}/{app.version}/add',
    'build_image': '/app/{app.name}/{app.version}/build',
    'test_app': '/app/{app.name}/{app.version}/test',
    'remove_app': '/app/{app.name}/{app.version}/remove',
}


def add_container(app, host):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['add_container'].format(app=app))
    daemon = app.is_daemon() and 'true' or 'false'
    data = {'host': host.ip, 'daemon': daemon}
    r = requests.post(url, data)
    return r.json()


def build_image(app, host, base):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['build_image'].format(app=app))
    data = {'host': host.ip, 'base': base, 'group': app.group}
    r = requests.post(url, data)
    return r.json()


def test_app(app, host):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['test_app'].format(app=app))
    data = {'host': host.ip}
    r = requests.post(url, data)
    return r.json()


def remove_app(app, host):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['remove_app'].format(app=app))
    data = {'host': host.ip}
    r = requests.post(url, data)
    return r.json()
