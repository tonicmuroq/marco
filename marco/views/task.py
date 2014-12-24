# coding: utf-8

from flask import Blueprint, request, abort, render_template, g, redirect

from marco.ext import openid2
from marco.models.task import Job


bp = Blueprint('task', __name__, url_prefix='/task')


@bp.route('/<task_id>/')
def task(task_id):
    st = Job.get(task_id)
    if not st:
        abort(404)
    limit = request.args.get('limit', type=int, default=300)
    logs = st.logs(size=limit)
    ws_url = g.pod.dot_ws_url + '/log?task=%s' % task_id
    return render_template('/task/task.html', st=st, logs=logs, ws_url=ws_url,
            app=st.appversion)


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
