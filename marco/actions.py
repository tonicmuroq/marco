# coding: utf-8

import requests
from urlparse import urljoin
from flask import current_app


API_FORMATS = {
    'register_app': '/app/{projectname}/{version}',
    'add_container': '/app/{app.name}/{app.version}/add',
    'build_image': '/app/{app.name}/{app.version}/build',
    'test_app': '/app/{app.name}/{app.version}/test',
    'remove_app': '/app/{app.name}/{app.version}/remove',
    'remove_container': '/container/{container.container_id}/remove',
}


_error = {
    'r': 1,
    'msg': '在执行其他任务呢',
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


def remove_container(container):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['remove_container'].format(container=container))
    r = requests.post(url)
    return r.json()


def register_app(projectname, version, group, appyaml, configyaml):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['register_app'].format(
        projectname=projectname, version=version))

    data = {'group': group, 'appyaml': appyaml, 'configyaml': configyaml}
    r = requests.post(url, data)
    return r.json()
