# coding: utf-8

from urlparse import urlparse
from werkzeug.utils import cached_property

from marco.ext import db
from marco.models.base import Base


class UserPod(Base):

    __tablename__ = 'user_pod'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    pod_id = db.Column(db.ForeignKey('pod.id'), primary_key=True)
    core_quota = db.Column(db.Integer)

    @cached_property
    def core_quota_used(self):
        from .host import Core
        return db.session.query(Core).filter(
            Core.pod_id == self.pod_id,
            Core.occupier_user_id == self.user_id).count()

    @classmethod
    def change_quota(cls, id, core_quota):
        p = db.session.query(cls).filter(cls.id == id).first()
        if p is not None:
            p.core_quota = core_quota
            db.session.add(p)
            db.session.commit()

    @classmethod
    def get_by_user_pod(cls, user_id, pod_id):
        return db.session.query(cls).filter(
            cls.user_id == user_id, cls.pod_id == pod_id).first()

class Pod(Base):

    __tablename__ = 'pod'

    name = db.Column(db.String(255), nullable=False, unique=True)
    users = db.relationship('User', secondary=UserPod.__table__)
    user_pods = db.relationship(UserPod)

    @classmethod
    def create(cls, name):
        try:
            p = cls(name=name)
            db.session.add(p)
            db.session.commit()
            return p
        except:
            return None

    @classmethod
    def get(cls, id):
        return db.session.query(cls).filter(cls.id == id).one()

    @classmethod
    def get_by_name(cls, name):
        return db.session.query(cls).filter(cls.name == name).one()

    @classmethod
    def get_all_pods(cls, start=0, limit=20):
        return db.session.query(cls).order_by(cls.id.asc()).offset(start).limit(limit).all()

    @cached_property
    def dots(self):
        return Dot.get_multi(pod_id=self.id)

    @cached_property
    def dot_url(self):
        dots = self.dots
        if not dots:
            return ''
        return dots[0].url

    @cached_property
    def etcd(self):
        dots = self.dots
        if not dots:
            return ''
        return dots[0].etcd

    @cached_property
    def es(self):
        dots = self.dots
        if not dots:
            return ''
        return dots[0].es

    @cached_property
    def influxdb(self):
        dots = self.dots
        if not dots:
            return ''
        return dots[0].influxdb

    @cached_property
    def dot_ws_url(self):
        dots = self.dots
        if not dots:
            return ''
        return dots[0].ws_url

    @cached_property
    def free_cores_in_pod(self):
        from .host import Host
        return [len(h.free_cores) for h in Host.all_hosts()]

    def add_user(self, user):
        if not user:
            return
        self.users.append(user)
        db.session.add(self)
        db.session.commit()


class User(Base):

    __tablename__ = 'user'

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    privilege = db.Column(db.Integer, nullable=False, default=0)
    pods = db.relationship('Pod', secondary=UserPod.__table__)

    @classmethod
    def get_or_create(cls, name, email):
        u = db.session.query(cls).filter(cls.email == email).first()
        if u:
            return u
        u = cls(name=name, email=email)
        db.session.add(u)
        db.session.commit()
        return u

    @classmethod
    def get_by_email(cls, email):
        return db.session.query(cls).filter(cls.email == email).one()

    @property
    def username(self):
        return self.name

    def add_pod(self, pod):
        if not pod:
            return
        self.pods.append(pod)
        db.session.add(self)
        db.session.commit()

    def is_admin(self):
        return self.privilege >= 6

    def set_privilege(self, privilege):
        self.privilege = privilege
        db.session.add(self)
        db.session.commit()


class Dot(Base):
    
    __tablename__ = 'dot'

    url = db.Column(db.String(255), nullable=False)
    es = db.Column(db.String(255), nullable=False)
    etcd = db.Column(db.String(255), nullable=False)
    influxdb = db.Column(db.String(255), nullable=False)
    pod_id = db.Column(db.Integer, nullable=False, default=0, index=True)

    @classmethod
    def create(cls, url, pod_id=0, es='', etcd='', influxdb=''):
        d = cls(url=url, pod_id=pod_id, es=es, etcd=etcd, influxdb=influxdb)
        db.session.add(d)
        db.session.commit()

    @classmethod
    def get_multi(cls, pod_id):
        return db.session.query(cls).filter(cls.pod_id == pod_id).all()

    @property
    def ws_url(self):
        parsed = urlparse(self.url)
        return 'ws://%s:%s' % (parsed.hostname, parsed.port)

UserPod.user = db.relationship(User)
UserPod.pod = db.relationship(Pod)
