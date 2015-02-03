from flask import Blueprint, request, render_template, abort, g, redirect

from marco.ext import openid2
from marco.models.host import Host, Core
from marco.models.pod import Pod

bp = Blueprint('host_adm', __name__, url_prefix='/host_adm')


@bp.route('/all', methods=['GET'])
def all_hosts():
    return render_template('/host/host_list.html', hosts=Host.all_hosts())


@bp.route('/one/<int:host_id>', methods=['GET'])
def one(host_id):
    return render_template('/host/one.html', host=Host.get(host_id))


@bp.route('/add_host', methods=['POST'])
def add_host():
    Node.create(request.form['host'], int(request.form['pod']))
    return redirect('/host_adm/all')


@bp.route('/add_core', methods=['POST'])
def add_core():
    Core.create(int(request.form['host']), g.pod.id, request.form['cpu_id'])
    return redirect('/host_adm/one/' + request.form['host'])


@bp.before_request
def test_if_logged_in():
    if not g.user:
        return redirect(openid2.login_url)
    if not g.user.is_admin():
        abort(403)
