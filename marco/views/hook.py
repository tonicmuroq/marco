# coding: utf-8

import json
import gitlab
from flask import request, Blueprint, current_app

from marco.actions import register_app
from marco.views.utils import jsonify
from marco.utils import yaml_to_json


bp = Blueprint(__name__, 'hook', url_prefix='/hook')


@bp.route('/gitlab/merge', methods=['POST', ])
@jsonify
def gitlab_merge():
    # TODO token 应该从 openid 取
    hd = json.loads(request.data)
    attrs = hd['object_attributes']
    if not (hd['object_kind'] == 'merge_request' 
            and attrs['state'] == 'merged'
            and attrs['target_branch'] == 'master'):
        return {'r': 1}

    git = gitlab.Gitlab(current_app.config['GITLAB_URL'],
            token=current_app.config['GITLAB_TOKEN'])
    project_id = attrs['target_project_id']
    project = git.getproject(project_id)
    repos = git.getrepositories(project_id)

    group = project['namespace']['name']
    projectname = project['name']
    version = repos[0]['commit']['id'][:7]

    appyaml = git.getrawblob(project_id, version, 'app.yaml') or ''
    configyaml = git.getrawblob(project_id, version, 'config.yaml') or ''

    register_app(projectname, version, group,
            yaml_to_json(appyaml), yaml_to_json(configyaml),
            project_id)

    return {'r': 0}
