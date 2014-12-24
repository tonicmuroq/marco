# coding: utf-8
from flask import (Blueprint, request, render_template,
        abort, g, redirect)

from marco.ext import openid2
from marco.models.pod import Pod, User, Dot


bp = Blueprint('pod', __name__, url_prefix='/pod')


@bp.route('/admin', methods=['POST', 'GET'])
def privilege_manage():
    if request.method == 'POST':
        p = request.form.get('privilege', type=int, default=0)
        email = request.form.get('email', type=str)
        u = User.get_by_email(email)
        if u:
            u.set_privilege(p)
    return render_template('/pod/admin.html')


@bp.route('/pods', methods=['POST', 'GET'])
def all_pods():
    if request.method == 'POST':
        name = request.form.get('name', type=str, default=0)
        if name:
            Pod.create(name)
    pods = Pod.get_all_pods()
    return render_template('/pod/pod_list.html', pods=pods)


@bp.route('/pod/<int:pod_id>/user', methods=['POST', 'GET'])
def pod_user(pod_id):
    pod = Pod.get(pod_id)
    if not pod:
        abort(404)
    if request.method == 'POST':
        email = request.form.get('email', type=str, default='')
        if email:
            user = User.get_by_email(email)
            pod.add_user(user)
    return render_template('/pod/pod_user.html', pod=pod)


@bp.route('/pod/<int:pod_id>/dot', methods=['POST', 'GET'])
def pod_dot(pod_id):
    pod = Pod.get(pod_id)
    if not pod:
        abort(404)
    if request.method == 'POST':
        dot_url = request.form.get('dot', type=str, default='')
        if dot_url:
            Dot.create(dot_url, pod_id)
    return render_template('/pod/pod_dot.html', pod=pod)


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
    # 太暴力
    if request.method == 'POST' and not g.user.is_admin():
        abort(403)
