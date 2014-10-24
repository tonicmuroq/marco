# coding: utf-8

from flask import request, Blueprint


bp = Blueprint(__name__, 'hook', url_prefix='/hook')


@bp.route('/gitlab/merge', methods=['POST', ])
def gitlab_merge():
    print request.form
    return ''
