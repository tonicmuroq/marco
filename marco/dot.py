# coding: utf-8

import requests
from urlparse import urljoin

session = requests.Session()


class DotClientError(Exception):

    def __init__(self, content, code):
        super(DotClientError, self).__init__('%s:%s' % (code, content))
        self.content = content
        self.code = code


class DotClient(object):

    def __init__(self, host='localhost', port=5000, timeout=5,
            scheme='http'):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._scheme = scheme
        self._base_url = '{0}://{1}:{2}'.format(
                self._scheme,
                self._host,
                self._port)

    def request(self, url, method='GET', params=None, data=None, json=True, expected_code=200):
        target_url = urljoin(self._base_url, url)
        resp = session.request(method=method, url=target_url, params=params,
                data=data, timeout=self._timeout)
        if resp.status_code != expected_code:
            raise DotClientError(resp.content, resp.status_code)
        if json:
            return resp.json()
        return resp.content

    def register(self, project_name, version, group, appyaml):
        url = '/app/%s/%s' % (project_name, version)
        data = {'group': group, 'appyaml': appyaml, 'configyaml': configyaml}
        return self.request(url, method='POST', data=data)

    def add_container(self, app, host, daemon=False):
        url = '/app/%s/%s/add' % (app.name, app.version)
        data = {'host': host.ip, 'daemon': str(daemon).lower()}
        return self.request(url, method='POST', data=data)
        
    def build_image(self, app, host, base):
        url = '/app/%s/%s/build' % (app.name, app.version)
        data = {'host': host.ip, 'base': base, 'group': app.group}
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

    def set_hook_branch(self, app_name, branch):
        url = '/app/%s/branch' % app_name
        data = {'branch': branch}
        return self.request(url, method='POST', data=data)

    def get_hook_branch(self, app_name):
        url = '/app/%s/branch' % app_name
        r = self.request(url, method='GET')
        return r['branch'] if not r['r'] else 'master'
