# coding: utf-8

import uuid
import functools
from werkzeug import cached_property

from marco.ext import db
from marco.ext import dot
from marco.models.base import Base


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

    @cached_property
    def cores(self):
        return Core.get_by_host(self.id)

    @cached_property
    def free_cores(self):
        return [c for c in self.cores if c.exclusive_uuid is None
                and c.bound_task is None and c.occupier_container_id is None]


class Core(Base):

    __tablename__ = 'host_core'

    id = db.Column(db.Integer, primary_key=True)
    cpu_id = db.Column(db.String(255), nullable=False)
    host_id = db.Column(db.Integer)
    pod_id = db.Column(db.Integer)
    exclusive_uuid = db.Column(db.String(255))
    bound_task = db.Column(db.Integer)
    occupier_container_id = db.Column(db.String(255))
    occupier_user_id = db.Column(db.Integer)

    @cached_property
    def occupier(self):
        from .container import Container
        return (None if self.occupier_container_id is None
                else Container.get_by_container_id(self.occupier_container_id))

    @classmethod
    def create(cls, host_id, pod_id, cpu_id):
        n = cls(host_id=host_id, pod_id=pod_id, cpu_id=cpu_id)
        db.session.add(n)
        db.session.commit()
        return n

    @classmethod
    def get_by_host(cls, host_id):
        return db.session.query(cls).filter(cls.host_id == host_id).all()

    @classmethod
    def occupy_cores(cls, cores, user_id):
        exclusive_uuid = str(uuid.uuid4())
        for c in cores:
            free_core = db.session.query(cls).filter(
                cls.id == c.id,
                cls.exclusive_uuid == None,
                cls.bound_task == None,
                cls.occupier_container_id == None,
            ).first()
            if free_core is None:
                raise ValueError('core unavailable')
            free_core.exclusive_uuid = exclusive_uuid
            free_core.occupier_user_id = user_id
            db.session.add(free_core)
        db.session.commit()

        # check if cores are locked by current procedure
        locked_cores = db.session.query(cls).filter(
            cls.exclusive_uuid == exclusive_uuid)
        if locked_cores.count() != len(cores):
            for c in locked_cores:
                c.exclusive_uuid = None
                c.occupier_user_id = None
                db.session.add(c)
            db.session.commit()
            raise ValueError('cores taken')

        return exclusive_uuid

    @classmethod
    def bind_to_task(cls, cores, task_id):
        for c in cores:
            c.bound_task = task_id
            db.session.add(c)
        db.session.commit()

    @classmethod
    def try_bind_container(cls, f):
        from .task import Job

        @functools.wraps(f)
        def g(*args, **kwargs):
            for c in db.session.query(cls).filter(
                    cls.occupier_container_id == None,
                    cls.bound_task != None):
                j = Job.get(c.bound_task)
                if j.success() and j.result:
                    c.bound_task = None
                    c.exclusive_uuid = None
                    c.occupier_container_id = j.result
                    db.session.add(c)
            db.session.commit()
            return f(*args, **kwargs)

        return g

    @classmethod
    def retire_cores_in_container(cls, container_id):
        for c in db.session.query(cls).filter(
                cls.occupier_container_id == container_id):
            c.occupier_container_id = None
            c.occupier_user_id = None
        db.session.commit()
