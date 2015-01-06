# coding: utf-8

import requests
from flask import g, has_request_context
from urlparse import urljoin

session = requests.Session()


class DotClientError(Exception):

    def __init__(self, content, code):
        super(DotClientError, self).__init__('%s:%s' % (code, content))
        self.content = content
        self.code = code


class DotClient(object):

    def __init__(self, host='localhost', port=5000, timeout=5,
            scheme='http', username=''):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._scheme = scheme
        self._base_url = '{0}://{1}:{2}'.format(
                self._scheme,
                self._host,
                self._port)
        self._username = username

    def _get_username(self):
        if has_request_context() and g.user:
            return g.user.username
        if self._username:
            return self._username
        raise RuntimeError('need username set')

    def request(self, url, method='GET', params={}, data=None, json=True, expected_code=200, need_user=True):
        if method == 'GET':
            need_user = False
        # set user
        headers = {'NBE-user': self._get_username() if need_user else 'NBEBot'}

        # set start/limit if none
        if 'start' not in params:
            params['start'] = 0
        if 'limit' not in params:
            params['limit'] = 20

        target_url = urljoin(self._base_url, url)
        resp = session.request(method=method, url=target_url, params=params,
                data=data, timeout=self._timeout, headers=headers)
        if resp.status_code != expected_code:
            raise DotClientError(resp.content, resp.status_code)
        if json:
            return resp.json()
        return resp.content

    def register(self, project_name, version, group, appyaml):
        url = '/app/%s/%s' % (project_name, version)
        data = {'group': group, 'appyaml': appyaml}
        return self.request(url, method='POST', data=data, need_user=False)

    def add_container(self, app, host, daemon='false'):
        url = '/app/%s/%s/add' % (app.name, app.version)
        data = {'host': host.ip, 'daemon': daemon}
        return self.request(url, method='POST', data=data)
        
    def build_image(self, app, host, base):
        url = '/app/%s/%s/build' % (app.name, app.version)
        data = {'host': host.ip, 'base': base, 'group': app.application.namespace}
        return self.request(url, method='POST', data=data)

    def test_app(self, app, host):
        url = '/app/%s/%s/test' % (app.name, app.version)
        data = {'host': host.ip}
        return self.request(url, method='POST', data=data)

    def remove_app(self, app, host):
        url = '/app/%s/%s/remove' % (app.name, app.version)
        data = {'host': host.ip}
        return self.request(url, method='POST', data=data)

    def update_app(self, app_name, from_version, to_version, hosts):
        url = '/app/%s/%s/update' % (app_name, from_version)
        data = {'to': to_version, 'hosts': hosts}
        return self.request(url, method='POST', data=data)

    def remove_container(self, container):
        url = '/container/%s/remove' % (container.container_id)
        return self.request(url, method='POST')

    def add_resource(self, app, resource, name, env='test'):
        if not resource in ('mysql', 'redis'):
            raise DotClientError('resource must be in mysql/redis', 400)
        if not env in ('prod', 'test'):
            raise DotClientError('env must be in prod/test', 400)
        url = '/resource/%s/%s' % (app, resource)
        data = {'name': name, 'env': env}
        return self.request(url, method='POST', data=data)

    def add_sentry(self, app_name, platform):
        url = '/resource/%s/sentry' % app_name
        data = {'platform': platform}
        return self.request(url, method='POST', data=data)

    def add_influxdb(self, app_name):
        url = '/resource/%s/influxdb' % app_name
        return self.request(url, method='POST')

    def set_hook_branch(self, app_name, branch):
        url = '/app/%s/branch' % app_name
        data = {'branch': branch}
        return self.request(url, method='PUT', data=data)

    def get_hook_branch(self, app_name):
        url = '/app/%s/branch' % app_name
        r = self.request(url)
        return r['branch'] if not r['r'] else 'master'

    def get_sentry_dsn(self, app_name, platform):
        url = '/resource/%s/sentry' % app_name
        data = {'platform': platform}
        return self.request(url, method='POST', data=data)

    def get_app(self, app_name):
        url = '/app/%s' % app_name
        return self.request(url)

    def get_apps(self, start=0, limit=20):
        params = {
            'start': start,
            'limit': limit,
        }
        return self.request('/app', params=params)

    def get_app_jobs(self, app_name, status=-1, succ=-1, start=0, limit=20):
        url = '/app/%s/jobs' % app_name
        params = {
            'status': status,
            'succ': succ,
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_app_containers(self, app_name, start=0, limit=20):
        url = '/app/%s/containers' % app_name
        params = {
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_app_versions(self, app_name, start=0, limit=20):
        url = '/app/%s/versions' % app_name
        params = {
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_appversion(self, name, version):
        url = '/appversion/%s/%s' % (name, version)
        return self.request(url)

    def get_appversion_by_id(self, id):
        url = '/appversion/%s' % id
        return self.request(url)

    def get_appversion_jobs(self, name, version, status=-1, succ=-1, start=0, limit=20):
        url = '/appversion/%s/%s/jobs' % (name, version)
        params = {
            'status': status,
            'succ': succ,
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_appversion_containers(self, name, version, start=0, limit=20):
        url = '/appversion/%s/%s/containers' % (name, version)
        params = {
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_host_by_id(self, id):
        url = '/host/%s' % id
        return self.request(url)

    def get_all_hosts(self, start=0, limit=20):
        url = '/hosts'
        params = {
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_container(self, cid):
        url = '/container/%s' % cid
        return self.request(url)

    def get_containers(self, host_id=-1, name='', version='', start=0, limit=20):
        url = '/containers'
        params = {
            'host_id': host_id,
            'name': name,
            'version': version,
            'start': start,
            'limit': limit,
        }
        return self.request(url, params=params)

    def get_job(self, id):
        url = '/job/%s' % id
        return self.request(url)

    def get_jobs(self, name, version='', status=-1, succ=-1, start=0, limit=20):
        params = {
            'name': name,
            'version': version,
            'status': status,
            'succ': succ,
            'start': start,
            'limit': limit,
        }
        return self.request('/jobs', params=params)
