# coding: utf-8

from flask.ext.navigator import Navigation

def _init_nav(nav):
    host_sub_nav = nav.Bar('host_sub_nav', [
        nav.Item(u'所有机器', 'host.index'),
    ])

    app_sub_nav = nav.Bar('app_sub_nav', [
        nav.Item(u'所有应用', 'app.index'),
    ])

    nav.Bar('marco_nav', [
        nav.Item(u'机器', 'host.index', sub_nav_bar=host_sub_nav),
        nav.Item(u'应用', 'app.index', sub_nav_bar=app_sub_nav),
    ])

def init_nav(app):
    nav = Navigation(app=app)
    _init_nav(nav)
