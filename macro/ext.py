# coding: utf-8

import os
import etcd as petcd


def create_etcd():
    etcd = os.environ['ETCD_ADDR']
    host, port = etcd.split(':')
    return petcd.Client(host=host, port=int(port))


etcd = create_etcd()
