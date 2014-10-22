# coding: utf-8

from flask import Blueprint, abort, render_template

from marco.ext import es
from marco.models.task import StoredTask


bp = Blueprint('task', __name__, url_prefix='/task')


@bp.route('/<task_id>/')
def task(task_id):
    st = StoredTask.get(task_id)
    if not st:
        abort(404)
    app = st.application
    query = 'apptype:test AND name:%s AND appid:%s' % (app.name, st.test_id)
    try:
        r = es.search(q=query)
        logs = ['{@timestamp}: {data}'.format(**d['_source']) for d in r['hits']['hits']]
    except:
        logs = []
    return render_template('/task/task.html', st=st, logs=logs)
