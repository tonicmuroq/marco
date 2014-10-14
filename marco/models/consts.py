# coding: utf-8

from enum import Enum


class TaskType(Enum):
    AddContainer = 1
    RemoveContainer = 2
    UpdateContainer = 3
    BuildImage = 4
    TestApplication = 5
    HostInfo = 6


class TaskStatus(Enum):
    Running = 0
    Done = 1


class TaskResult(Enum):
    Succ = 0
    Fail = 1
