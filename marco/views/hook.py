# coding: utf-8

import json
import gitlab
from urlparse import urlparse
from flask import request, Blueprint, current_app

from marco.actions import register_app
from marco.views.utils import jsonify
from marco.utils import yaml_to_json


bp = Blueprint(__name__, 'hook', url_prefix='/hook')


@bp.route('/gitlab/merge', methods=['POST', ])
@jsonify
def gitlab_merge():
    # TODO token 应该从 openid 取
    git = gitlab.Gitlab(current_app.config['GITLAB_URL'],
            token=current_app.config['GITLAB_TOKEN'])
    hd = json.loads(request.data)
    u = urlparse(hd['repository']['homepage'])

    group = u.path.split('/')[1]
    projectname = hd['repository']['name']
    version = hd['after'][:7]

    appyaml = git.getrawblob(hd['project_id'], hd['after'], 'app.yaml') or ''
    configyaml = git.getrawblob(hd['project_id'], hd['after'], 'config.yaml') or ''

    register_app(projectname, version, group,
            yaml_to_json(appyaml), yaml_to_json(configyaml))

    return {'r': 0}
