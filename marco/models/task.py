# coding: utf-8

import arrow
from werkzeug import cached_property

from marco.ext import dot, es
from marco.models.consts import TaskType, TaskStatus, TaskResult


repr_dict = {
    TaskType.AddContainer: u'增加容器',
    TaskType.RemoveContainer: u'下线容器',
    TaskType.UpdateContainer: u'更新容器',
    TaskType.BuildImage: u'构建镜像',
    TaskType.TestApplication: u'测试应用',
    TaskType.HostInfo: u'请求host信息',
}


apptype_dict = {
    TaskType.TestApplication: 'test',
    TaskType.BuildImage: 'build',
}


class Job(object):

    def __init__(self, id, app_name, app_version, status, succ,
            kind, result, created, finished):
        self.id = id
        self.app_name = app_name
        self.app_version = app_version
        self.status = status
        self.succ = succ
        self.kind = kind
        self.result = result
        self.created = arrow.get(created).datetime
        self.finished = finished and arrow.get(finished).datetime or None

    @classmethod
    def get(cls, id):
        job = dot.get_job(id)
        if job:
            return cls(**job)

    @classmethod
    def get_multi(cls, app_name, app_version='', status=-1, succ=-1, start=0, limit=20):
        jobs = dot.get_jobs(app_name, app_version, status, succ, start, limit)
        return [cls(**job) for job in jobs]

    def success(self):
        return TaskResult(self.succ) == TaskResult.Succ

    def processing(self):
        return self.status == TaskStatus.Running.value

    def repr(self):
        return '%s: %s' % (self.create_time(), self.kind_cn())

    def create_time(self):
        return self.created.strftime('%Y-%m-%d %H:%M:%S')

    def finish_time(self):
        return self.finished and self.finished.strftime('%Y-%m-%d %H:%M:%S') or ''

    def kind_cn(self):
        return repr_dict[TaskType(self.kind)]

    def logs(self, size=100, timeout=1):
        apptype = apptype_dict.get(TaskType(self.kind), '')
        if not apptype:
            return []
        q = 'apptype:%s AND name:%s AND id:%s' % (apptype, self.app_name, self.id)
        r = es.search(q=q, size=size, sort='count', timeout=timeout)
        try:
            logs = [d['_source']['data'] for d in r['hits']['hits']]
        except:
            logs = []
        return logs

    @cached_property
    def application(self):
        from .application import Application
        return Application.get_by_name(self.app_name)

    @cached_property
    def appversion(self):
        from .application import AppVersion
        return AppVersion.get_by_name_and_version(self.app_name, self.app_version)

    @cached_property
    def test_id(self):
        if TaskType(self.kind) != TaskType.TestApplication:
            return ''
        return self.result.split('|', 1)[0]
