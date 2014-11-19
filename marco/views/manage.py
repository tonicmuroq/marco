# coding: utf-8

import yaml
import urllib
import urlparse
from flask import Blueprint, request, render_template, flash, redirect, url_for

from marco.ext import gitlab, dot
from marco.utils import yaml_to_json


bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/')
def index():
    return redirect(url_for('manage.create_app'))


@bp.route('/create', methods=['GET', 'POST'])
def create_app():
    if request.method == 'POST':
        name = request.form.get('name', type=str)
        runtime = request.form.get('runtime', type=str)
        namespace_id = request.form.get('namespace', type=str)
        project = create_nbe_app(name, runtime, namespace_id)
        if project:
            return render_template('/manage/create_done.html',
                    project_url=project['web_url'], name=project['name'])

    namespaces = gitlab.getgroups() or []
    return render_template('/manage/create.html', namespaces=namespaces)


@bp.route('/import', methods=['GET', 'POST'])
def import_app():
    if request.method == 'POST':
        addr = request.form.get('addr', type=str)
        runtime = request.form.get('runtime', type=str)
        appyaml = request.form.get('appyaml', type=str, default='off')
        
        project = import_nbe_app(addr, runtime, appyaml=='on')
        if project:
            return render_template('/manage/create_done.html',
                    project_url=project['web_url'], name=project['name'])
        flash(u'导入失败', 'error')
    return render_template('/manage/import.html')


def create_nbe_app(name, runtime, namespace_id):
    app_dict = {'appname': name, 'runtime': runtime}
    app_yaml = yaml.safe_dump(app_dict, default_flow_style=False)

    project = gitlab.createproject(name, namespace_id, issues_enabled=1,
            wall_enabled=1, merge_requests_enabled=1, wiki_enabled=1,
            snippets_enabled=1, public=1)
    if not project:
        flash(u'项目创建失败', 'error')
        return
    # 这绝逼失败的好么, gitlab 也没给个创建分支的API
    if not gitlab.createfile(project['id'], 'app.yaml', 'master', app_yaml, 'NBE AutoCommit'):
        flash(u'app.yaml创建失败', 'error')
        return
    if not gitlab.addprojecthook(project['id'], 'http://marco.intra.hunantv.com/hook/gitlab/merge'):
        flash(u'hook创建失败', 'error')
        return
    return project


def import_nbe_app(addr, runtime, with_app_yaml=True):
    parsed = urlparse.urlparse(addr)
    if not parsed.path:
        flash(u'Gitlab 地址格式不对, 请填写项目的URL', 'error')
        return

    project = gitlab.getproject(urllib.quote(parsed.path[1:], safe=''))
    if not project:
        flash(u'项目导入失败, 真的有这个项目咩?', 'error')
        return

    project_id = project['id']
    project_name = project['name']

    if with_app_yaml:
        app_yaml = render_template('/nbe/app.yaml',
                name=project_name, runtime=runtime)
        if not gitlab.createfile(project_id, 'app.yaml',
                'master', app_yaml, 'NBE: Create app.yaml'):
            flash(u'app.yaml 创建失败', 'error')
            return

    if not gitlab.addprojecthook(project['id'], 'http://marco.intra.hunantv.com/hook/gitlab/merge',
            merge_requests=True):
        flash(u'hook创建失败', 'error')
        return

    commits = gitlab.listrepositorycommits(project_id, page=0)
    if commits:
        version = commits[0]['id'][:7]
        group = project['namespace']['name']
        app_yaml = gitlab.getrawblob(project_id, version, 'app.yaml')
        if not app_yaml:
            app_yaml = render_template('/nbe/app.yaml',
                    name=project_name, runtime=runtime)
        dot.register(project_name, version, group, yaml_to_json(app_yaml))

    return project
