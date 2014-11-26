# coding: utf-8

from flask import g, redirect, Blueprint, render_template

from marco.ext import openid2, gitlab


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    if not g.user:
        return redirect(openid2.login_url)
    namespaces = gitlab.getgroups() or []
    return render_template('/index.html', namespaces=namespaces)
