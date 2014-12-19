# coding: utf-8

from werkzeug import cached_property

from marco.ext import dot


class Host(object):

    def __init__(self, id, ip, name, status):
        self.id = id
        self.ip = ip
        self.name = name
        self.status = status

    @classmethod
    def get(cls, id):
        host = dot.get_host_by_id(id)
        if host:
            return cls(**host)

    @classmethod
    def all_hosts(cls, start=0, limit=20):
        hosts = dot.get_all_hosts(start, limit)
        return [cls(**host) for host in hosts if host]

    def is_online(self):
        return self.status == 0

    @cached_property
    def containers(self):
        from .container import Container
        return Container.get_multi(host_id=self.id)

    @cached_property
    def apps(self):
        from .application import Application
        app_ids = list(set(c.app_id for c in self.containers))
        return filter(None, [Application.get(i) for i in app_ids])
