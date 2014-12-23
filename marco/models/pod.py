# coding: utf-8

from marco.ext import db
from marco.models.base import Base


class Pod(Base):

    __tablename__ = 'pod'

    name = db.Column(db.String(255), nullable=False, unique=True)

    @classmethod
    def create(cls, name):
        p = cls(name=name)
        db.session.add(p)
        db.session.commit()
        return p

    @classmethod
    def get_by_name(cls, name):
        return db.session.query(cls).filter(cls.name == name).one()

    @property
    def dots(self):
        return Dot.get_multi(pod_id=self.id)


class UserPod(db.Model):

    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    pod_id = db.Column(db.ForeignKey('pod.id'), primary_key=True)


class User(Base):

    __tablename__ = 'user'

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    pods = db.relationship(Pod, secondary=UserPod.__table__)

    @classmethod
    def get_or_create(cls, name, email):
        u = db.session.query(cls).filter(cls.email == email).one()
        if u:
            return u
        u = cls(name=name, email=email)
        db.session.add(u)
        db.session.commit()
        return u

    def add_pod(self, pod):
        self.pods.append(pod)
        db.session.add(self)
        db.session.commit()


class Dot(Base):
    
    __tablename__ = 'dot'

    url = db.Column(db.String(255), nullable=False)
    pod_id = db.Column(db.Integer, nullable=False, default=0)

    @classmethod
    def create(cls, url, pod_id=0):
        d = cls(url=url, pod_id=pod_id)
        db.session.add(d)
        db.session.commit()

    @classmethod
    def get_multi(cls, pod_id):
        return db.session.query(cls).filter(cls.pod_id == pod_id).all()
