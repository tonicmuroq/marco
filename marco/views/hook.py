# coding: utf-8

import json
from urlparse import urlparse
from flask import request, Blueprint

from marco.ext import gitlab
from marco.dot import DotClient
from marco.views.utils import jsonify
from marco.utils import yaml_to_json

from marco.models.pod import Pod


bp = Blueprint(__name__, 'hook', url_prefix='/hook')


@bp.route('/gitlab/merge', methods=['POST', ])
@jsonify
def gitlab_merge():
    # TODO token 应该从 openid 取
    pod_name = request.args.get('pod', default='intra', type=str)
    pod = Pod.get_by_name(pod_name)
    if not pod:
        return {'r': 1, 'msg': 'pod not exists'}
    if not pod.dot_url:
        return {'r': 1, 'msg': 'pod not initialized'}

    parsed = urlparse(pod.dot_url)
    dot = DotClient(host=parsed.hostname, port=parsed.port, scheme=parsed.scheme)

    hd = json.loads(request.data)
    attrs = hd['object_attributes']
    if not (hd['object_kind'] == 'merge_request' 
            and attrs['state'] == 'merged'):
        return {'r': 1, 'msg': 'must be merged'}

    project_id = attrs['target_project_id']
    project = gitlab.getproject(project_id)

    group = project['namespace']['name']
    projectname = project['name']
    version = gitlab.listrepositorycommits(project_id, page=0)[0]['id'][:7]

    appyaml = gitlab.getrawblob(project_id, version, 'app.yaml') or ''

    if attrs['target_branch'] != 'master':
        return {'r': 1, 'msg': 'must be merged into master'}

    dot.register(projectname.lower(), version, group.lower(),
            yaml_to_json(appyaml))

    return {'r': 0, 'msg': 'ok'}
