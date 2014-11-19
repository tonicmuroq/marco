# coding: utf-8

import json
from flask import request, Blueprint

from marco.ext import dot, gitlab
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
    project_id = attrs['target_project_id']
    project = gitlab.getproject(project_id)

    group = project['namespace']['name']
    projectname = project['name']
    version = gitlab.listrepositorycommits(project_id, page=0)[0]['id'][:7]

    appyaml = gitlab.getrawblob(project_id, version, 'app.yaml') or ''

    appyaml_dict = yaml_loads(appyaml)
    if attrs['target_branch'] != dot.get_hook_branch(appyaml_dict.get('appname')):
        return {'r': 1}

    dot.register(projectname.lower(), version, group.lower(),
            yaml_to_json(appyaml))

    return {'r': 0}
