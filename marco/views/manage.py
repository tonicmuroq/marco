# coding: utf-8

import yaml
import urllib
import urlparse
from flask import Blueprint, request, render_template

from marco.ext import gitlab, dot
from marco.views.utils import jsonify
from marco.utils import yaml_to_json

HOOK_URL = 'http://marco.intra.hunantv.com/hook/gitlab/merge'

bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/create', methods=['POST'])
@jsonify
def create_app_ajax():
    name = request.form.get('name', type=str)
    runtime = request.form.get('runtime', type=str)
    namespace_id = request.form.get('namespace', type=str)
    error, project = create_nbe_app(name.lower(), runtime, namespace_id)
    return {'r': int(bool(error)), 'error': error, 'project': project}


@bp.route('/import', methods=['POST'])
@jsonify
def import_app_ajax():
    addr = request.form.get('addr', type=str)
    runtime = request.form.get('runtime', type=str)
    appyaml = request.form.get('appyaml', type=int, default=0)
    error, project = import_nbe_app(addr, runtime, appyaml)
    return {'r': int(bool(error)), 'error': error, 'project': project}


def create_nbe_app(name, runtime, namespace_id):
    app_dict = {'appname': name, 'runtime': runtime}
    app_yaml = yaml.safe_dump(app_dict, default_flow_style=False)

    project = gitlab.createproject(name, namespace_id, issues_enabled=1,
            wall_enabled=1, merge_requests_enabled=1, wiki_enabled=1,
            snippets_enabled=1, public=1)
    if not project:
        return u'项目创建失败', None

    # 这绝逼失败的好么, gitlab 也没给个创建分支的API
    if not gitlab.createfile(project['id'], 'app.yaml', 'master', app_yaml, 'NBE AutoCommit'):
        return u'app.yaml创建失败', None

    hooks = gitlab.getprojecthooks(project['id'])
    has_hook = any(h['url'] == HOOK_URL and h['merge_requests_events'] for h in hooks)
    if not has_hook:
        if not gitlab.addprojecthook(project['id'], 'http://marco.intra.hunantv.com/hook/gitlab/merge'):
            return u'hook创建失败', None

    return u'', project


def import_nbe_app(addr, runtime, with_app_yaml=False):
    parsed = urlparse.urlparse(addr)
    if not parsed.path:
        return u'Gitlab 地址格式不对, 请填写项目的URL', None

    project = gitlab.getproject(urllib.quote(parsed.path[1:], safe=''))
    if not project:
        return u'项目导入失败, 真的有这个项目咩?', None

    project_id = project['id']
    project_name = project['name'].lower()

    if with_app_yaml:
        app_yaml = render_template('/nbe/app.yaml', name=project_name, runtime=runtime)
        # 如果又要创建 app.yaml 又没有一个 master 分支的话是肯定会挂的
        if not gitlab.createfile(project_id, 'app.yaml', 'master', app_yaml, 'NBE: Create app.yaml'):
            return u'app.yaml 创建失败', None

    hooks = gitlab.getprojecthooks(project_id)
    has_hook = any(h['url'] == HOOK_URL and h['merge_requests_events'] for h in hooks)
    if not has_hook:
        if not gitlab.addprojecthook(project_id, HOOK_URL, merge_requests=True):
            return u'hook创建失败', None

    commits = gitlab.listrepositorycommits(project_id, page=0)
    if commits:
        version = commits[0]['id'][:7]
        group = project['namespace']['name']
        app_yaml = gitlab.getrawblob(project_id, version, 'app.yaml')
        if not app_yaml:
            app_yaml = render_template('/nbe/app.yaml', name=project_name, runtime=runtime)
        dot.register(project_name, version, group, yaml_to_json(app_yaml))

    return u'', project
