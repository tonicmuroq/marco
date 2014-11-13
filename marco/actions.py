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
    'update_app': '/app/{name}/{from_version}/update',
    'remove_container': '/container/{container.container_id}/remove',
    'add_mysql': '/resource/{app.name}/{app.version}/mysql',
    'hook_branch': '/app/{app}/branch',
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
    print r.json()
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


def sync_database(app, sql):
    target_url = current_app.config['DB_MANAGER_URL']
    data = {
        'DbUid': app.name,
        'businessCode': 'AutoUpdate',
        'DbName': app.name,
        'SysUid': 'CreateDbUser',
        'SysPwd': 'CreateDbUser',
        'SqlScript': sql,
    }
    r = requests.post(urljoin(target_url, 'InitDataBase.aspx'), data)
    return r.json()


def update_app_to_version(name, from_version, to_version, hosts):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['update_app'].format(name=name,
            from_version=from_version))
    data = {'to': to_version, 'hosts': hosts}
    r = requests.post(url, data)
    return r.json()


def add_mysql(app):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['add_mysql'].format(app=app))
    r = requests.post(url)
    return r.json()


def set_hook_branch(app, branch):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['hook_branch'].format(app=app))
    r = requests.put(url, {'branch': branch})
    return r.json()


def get_hook_branch(app):
    target_url = current_app.config['DOT_URL']
    url = urljoin(target_url, API_FORMATS['hook_branch'].format(app=app))
    r = requests.get(url)
    r = r.json()
    return r['branch'] if not r['r'] else 'master'
