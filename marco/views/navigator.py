# coding: utf-8

from flask.ext.navigator import Navigation

def _init_nav(nav):
    host_sub_nav = nav.Bar('marco_host_nav', [
        nav.Item(u'容器列表', 'host.index'),
    ])

    nav.Bar('marco_nav', [
        nav.Item(u'机器', 'host.index', sub_nav_bar=host_sub_nav),
    ])

def init_nav(app):
    nav = Navigation(app=app)
    _init_nav(nav)
