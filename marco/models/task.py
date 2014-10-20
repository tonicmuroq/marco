# coding: utf-8

from marco.ext import db

from marco.models.consts import TaskType, TaskStatus
from marco.models.base import Base


repr_dict = {
    TaskType.AddContainer: u'增加容器',
    TaskType.RemoveContainer: u'下线容器',
    TaskType.UpdateContainer: u'更新容器',
    TaskType.BuildImage: u'构建镜像',
    TaskType.TestApplication: u'测试应用',
    TaskType.HostInfo: u'请求host信息',
}


class StoredTask(Base):

    __tablename__ = 'stored_task'

    app_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    succ = db.Column(db.Integer, nullable=False)
    kind = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)

    @classmethod
    def get_multi(cls, app_id, status=None, succ=None, start=0, limit=20):
        q = db.session.query(cls).filter(cls.app_id == app_id)        
        if status is not None:
            q = q.filter(cls.status == status.value)
        if succ is not None:
            q = q.filter(cls.succ == succ.value)
        q = q.order_by(cls.id.desc()).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def processing(self):
        return self.status == TaskStatus.Running.value

    def repr(self):
        time_str = self.created.strftime('%Y-%m-%d %H:%M:%S')
        return '%s: %s' % (time_str, repr_dict[TaskType(self.kind)])
