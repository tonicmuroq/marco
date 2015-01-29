# coding: utf-8

from werkzeug import cached_property

from marco.ext import dot


class Container(object):

    def __init__(self, id, container_id, port, host_id, ident_id, app_name, version, sub_app):
        self.id = id
        self.container_id = container_id
        self.port = port
        self.host_id = host_id
        self.ident_id = ident_id
        self.app_name = app_name
        self.version = version
        self.sub_app = sub_app

    @classmethod
    def get_by_container_id(cls, cid):
        if not cid:
            return None
        c = dot.get_container(cid)
        if c:
            return cls(**c)

    @classmethod
    def get_multi(cls, host_id=-1, app_name='', version='', start=0, limit=20):
        cs = dot.get_containers(host_id, app_name, version, start, limit)
        return [cls(**c) for c in cs if c]

    @classmethod
    def get_multi_by_app_name(cls, app_name, start=0, limit=20):
        cs = dot.get_containers(cls, name=app_name, start=start, limit=limit)
        return [cls(**c) for c in cs if c]

    @cached_property
    def application(self):
        from .application import Application
        return Application.get_by_name(self.app_name)

    @cached_property
    def appversion(self):
        from .application import AppVersion
        return AppVersion.get_by_name_and_version(self.app_name, self.version)

    @cached_property
    def host(self):
        from .host import Host
        return Host.get(self.host_id)
