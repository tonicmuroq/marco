# coding: utf-8

from flask import g, redirect, url_for, Blueprint

from marco.ext import openid2


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    if g.user:
        return redirect(url_for('host.index'))
    return redirect(openid2.login_url)
