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
        self._headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
        }

    def request(self, url, method='GET', params=None, data=None, json=True, expected_code=200):
        url = '{0}/{1}'.format(self._base_url, url)
        resp = session.request(method=method, url=url, params=params,
                data=data, headers=self._headers, timeout=self._timeout)
        if resp.status_code != expected_code:
            raise DotClientError(resp.content, resp.status_code)
        if json:
            return resp.json()
        return resp.content

    def register(self, project_name, version, group, appyaml):
        url = '%s/app/%s/%s' % (self._base_url, project_name, version)
        data = {'group': group, 'appyaml': appyaml, 'configyaml': configyaml}
        return self.request(url, method='POST', data=data)

    def add_container(self, app, host, daemon=False):
        url = '%s/app/%s/%s/add' % (self._base_url, app.name, app.version)
        data = {'host': host.ip, 'daemon': str(daemon).lower()}
        return self.request(url, method='POST', data=data)
        
    def build_image(self, app, host, base):
        url = '%s/app/%s/%s/build' % (self._base_url, app.name, app.version)
        data = {'host': host.ip, 'base': base, 'group': app.group}
        return self.request(url, method='POST', data=data)

    def test_app(self, app, host):
        url = '%s/app/%s/%s/test' % (self._base_url, app.name, app.version)
        data = {'host': host.ip}
        return self.request(url, method='POST', data=data)

    def remove_app(self, app, host):
        url = '%s/app/%s/%s/remove' % (self._base_url, app.name, app.version)
        data = {'host': host.ip}
        return self.request(url, method='POST', data=data)

    def update_app(self, app_name, from_version, to_version, hosts):
        url = '%s/app/%s/%s/update' % (self._base_url, app_name, from_version)
        data = {'to': to_version, 'hosts': hosts}
        return self.request(url, method='POST', data=data)

    def remove_container(self, container):
        url = '%s/container/%s/remove' % (self._base_url, container.container_id)
        return self.request(url, method='POST')

    def add_resource(self, app, resource, name, env='test'):
        if not resource in ('mysql', 'redis'):
            raise DotClientError('resource must be in mysql/redis', 400)
        if not env in ('prod', 'test'):
            raise DotClientError('env must be in prod/test', 400)
        url = '%s/resource/%s/%s/%s' % (self._base_url, app.name, app.version, resource)
        data = {'name': name, 'env': env}
        return self.request(url, method='POST', data=data)

    def set_hook_branch(self, app, branch):
        url = '%s/app/%s/branch' % (self._base_url, app.name)
        data = {'branch': branch}
        return self.request(url, method='POST', data=data)

    def get_hook_branch(self, app):
        url = '%s/app/%s/branch' % (self._base_url, app.name)
        r = self.request(url, method='GET')
        return r['branch'] if not r['r'] else 'master'
