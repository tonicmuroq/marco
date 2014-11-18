# coding: utf-8

import yaml
from flask import Blueprint, request, render_template, flash, redirect, url_for

from marco.ext import gitlab


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
        project_url = create_nbe_app(name, runtime, namespace_id)
        if project_url:
            return render_template('/manage/create_done.html', project_url=project_url, name=name)

    namespaces = gitlab.getgroups() or []
    return render_template('/manage/create.html', namespaces=namespaces)


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
    return project['web_url']
