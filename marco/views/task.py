# coding: utf-8

from flask import Blueprint, abort, render_template

from marco.models.task import StoredTask

bp = Blueprint('task', __name__, url_prefix='/task')


@bp.route('/<task_id>/')
def task(task_id):
    st = StoredTask.get(task_id)
    if not st:
        abort(404)
    return render_template('/task/task.html', st=st)
