# -*- coding: utf-8 -*-
import gevent
from gevent import monkey, pool
monkey.patch_all()

import unittest, random, json, time
from pymongo import IndexModel
from melee.nosql.mongodb import BaseMongoMultiClientIndexModel
from melee.core.env import config

clients = config.mongodb_clients


class MongoMultiClientIndexModelDemo(BaseMongoMultiClientIndexModel):
    __db_name__ = 'testcase'
    __collection_name__ = 'testcaseschool'

    __attrs__ = ['mid', 'name', 'loc', 'daxue', 'xiaoqu', 'xueyuan', 'gender', 'ut']

    __keys__ = ['mid']

    __indexes__ = [
        IndexModel([('mid', 1)], name='user_index', unique=True),
        IndexModel([('loc', '2dsphere')], name='user_loc_index'),
        IndexModel([('daxue', 1), ('xiaoqu', 1), ('xueyuan', 1)], name='user_school_index'),
        IndexModel([('name', 1)], name='user_name_index'),
        IndexModel([('gender', 1)], name='user_gender_index'),
        IndexModel([('ut', -1)], name='ut_index')
    ]

p = pool.Pool(2000)

class TestIndexLoad(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        MongoMultiClientIndexModelDemo.create_index()

    @classmethod
    def tearDownClass(cls):
        # for db in MongoMultiClientIndexModelDemo.__dbs__:
        #     db.drop_collection(MongoMultiClientIndexModelDemo.__collection_name__)
        pass

    def _write(self, workerid, total, count_per_second):
        def _write_one():
            mid = str(int(time.time()*1000) + random.randint(10000,90000))
            d = MongoMultiClientIndexModelDemo(mid=mid)
            d.name = str('name%s' % random.randint(1,100000))
            d.loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)]
            d.daxue = str(random.randint(100,200))
            d.xiaoqu = str(random.randint(10,20))
            d.xueyuan = str(random.randint(1000,2000))
            d.gender = str(random.randint(1,2))
            d.save()
        count = 0
        while True:
            startms = int(time.time()*1000)
            for i in xrange(count_per_second):
                p.spawn(_write_one)
                count += 1
            endms = int(time.time()*1000)
            if (endms-startms) > 1000:
                print '----------------------WARNING: TOO SLOW NOW -----------------------'
            else:
                gevent.sleep((endms-startms)/1000.0)
                print '--------------------------WORKER %s write %s of %s/%s, sleep %sms------------------------' % (workerid, count_per_second, count, total, (endms-startms))
            if count >= total:
                break
        print '----------------END-------------------'


    def test_write(self):
        for i in xrange(10):
            p.spawn(self._write(i, 10000, 10))
        p.join()

    def _query(self, workerid, total, count_per_second):
        def _query_one():
            gender = str(random.randint(1,2))
            daxue = str(random.randint(100,200))
            ds = MongoMultiClientIndexModelDemo.find({'gender':gender, 'daxue':daxue}, limit=20, skip=random.randint(20,40))

        count = 0
        while True:
            startms = int(time.time()*1000)
            for i in xrange(count_per_second):
                p.spawn(_query_one)
                count += 1
            endms = int(time.time()*1000)
            if (endms-startms) > 1000:
                print '----------------------WARNING: TOO SLOW NOW -----------------------'
            else:
                gevent.sleep((endms-startms)/1000.0)
                print '--------------------------WORKER %s find %s of %s/%s, sleep %sms------------------------' % (workerid, count_per_second, count, total, (endms-startms))
            if count >= total:
                break
        print '----------------END-------------------'

    def test_query(self):
        for i in xrange(10):
            # pass
            p.spawn(self._query(i, 1000, 10))
        p.join()



