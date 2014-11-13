# coding: utf-8

import json
import gitlab
from flask import request, Blueprint, current_app

from marco.actions import register_app, get_hook_branch
from marco.views.utils import jsonify
from marco.utils import yaml_to_json, yaml_loads


bp = Blueprint(__name__, 'hook', url_prefix='/hook')


@bp.route('/gitlab/merge', methods=['POST', ])
@jsonify
def gitlab_merge():
    # TODO token 应该从 openid 取
    hd = json.loads(request.data)
    attrs = hd['object_attributes']
    if not (hd['object_kind'] == 'merge_request' 
            and attrs['state'] == 'merged'):
        return {'r': 1}
    git = gitlab.Gitlab(current_app.config['GITLAB_URL'],
            token=current_app.config['GITLAB_TOKEN'])
    project_id = attrs['target_project_id']
    project = git.getproject(project_id)

    group = project['namespace']['name']
    projectname = project['name']
    version = git.listrepositorycommits(project_id)[0]['id'][:7]

    appyaml = git.getrawblob(project_id, version, 'app.yaml') or ''
    configyaml = git.getrawblob(project_id, version, 'config.yaml') or ''

    appyaml_dict = yaml_loads(appyaml)
    if attrs['target_branch'] != get_hook_branch(appyaml_dict.get('appname')):
        return {'r': 1}

    register_app(projectname.lower(), version, group.lower(),
            yaml_to_json(appyaml), yaml_to_json(configyaml))

    return {'r': 0}
