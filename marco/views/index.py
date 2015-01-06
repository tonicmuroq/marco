# coding: utf-8

from flask import g, redirect, Blueprint, render_template

from marco.ext import openid2
from marco.models.application import Application


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    if not g.user:
        return redirect(openid2.login_url)
    app_names = Application.get_all_app_names(limit=20)
    # namespaces = gitlab.getgroups() or []
    # return render_template('/index.html', namespaces=namespaces)
    # return render_template('/app/app_base.html', namespaces=namespaces)
    return render_template('dashboard.html', app_names=app_names)


@bp.route('/_sentry')
def test_sentry():
    1/0
    return 'test_sentry'
