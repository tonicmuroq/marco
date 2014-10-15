# coding: utf-8

from flask import redirect, url_for, Blueprint


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    return redirect(url_for('host.index'))
