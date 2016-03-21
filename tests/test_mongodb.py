# -*- coding: utf-8 -*-

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


class TestIndex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        MongoMultiClientIndexModelDemo.create_index()

    @classmethod
    def tearDownClass(cls):
        # for db in MongoMultiClientIndexModelDemo.__dbs__:
        #     db.drop_collection(MongoMultiClientIndexModelDemo.__collection_name__)
        pass
    
    def test_save(self):
        mid = str(int(time.time()*1000))
        d = MongoMultiClientIndexModelDemo(mid=mid)
        d.name = str('name%s' % random.randint(1,100000))
        d.loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)]
        d.daxue = str(random.randint(100,200))
        d.xiaoqu = str(random.randint(10,20))
        d.xueyuan = str(random.randint(1000,2000))
        d.gender = str(random.randint(1,2))
        count = d.save()
        self.assertEqual(count, len(clients))

        doc = dict(
            name = str('name%s' % random.randint(1,100000)),
            loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)],
            daxue = str(random.randint(100,200)),
            xiaoqu = str(random.randint(10,20)),
            xueyuan = str(random.randint(1000,2000)),
            gender = str(random.randint(1,2)),
        )
        d.name = doc.get('name')
        d.loc = doc.get('loc')
        d.daxue = doc.get('daxue')
        d.xiaoqu = doc.get('xiaoqu')
        d.xueyuan = doc.get('xueyuan')
        d.gender = doc.get('gender')
        count = d.save()
        self.assertEqual(count, len(clients))
        d = MongoMultiClientIndexModelDemo(mid=mid)
        for k in ['name', 'loc', 'daxue', 'xiaoqu', 'xueyuan', 'gender']:
            print '%s: %s|%s' % (k, getattr(d, k), doc.get(k))
            self.assertEqual(getattr(d, k), doc.get(k))


    def test_replace(self):
        mid = str(int(time.time()*1000))
        d = MongoMultiClientIndexModelDemo(mid=mid)
        d.name = str('name%s' % random.randint(1,100000))
        d.loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)]
        d.daxue = str(random.randint(100,200))
        d.xiaoqu = str(random.randint(10,20))
        d.xueyuan = str(random.randint(1000,2000))
        d.gender = str(random.randint(1,2))
        count = d.save()
        self.assertEqual(count, len(clients))

        doc = dict(
            name = str('name%s' % random.randint(1,100000)),
            loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)],
            daxue = str(random.randint(100,200)),
            xiaoqu = str(random.randint(10,20)),
            xueyuan = str(random.randint(1000,2000)),
            gender = str(random.randint(1,2)),
        )
        count = d.replace(doc)
        self.assertEqual(count, len(clients))

        d = MongoMultiClientIndexModelDemo(mid=mid)
        for k in ['name', 'loc', 'daxue', 'xiaoqu', 'xueyuan', 'gender']:
            print '%s: %s|%s' % (k, getattr(d, k), doc.get(k))
            self.assertEqual(getattr(d, k), doc.get(k))


    def test_find(self):
        mid = str(int(time.time()*1000))
        d = MongoMultiClientIndexModelDemo(mid=mid)
        d.name = str('name%s%s' % (time.time(), random.randint(1,100000)))
        d.loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)]
        d.daxue = str(random.randint(100,200))
        d.xiaoqu = str(random.randint(10,20))
        d.xueyuan = str(random.randint(1000,2000))
        d.gender = str(random.randint(1,2))
        count = d.save()
        self.assertEqual(count, len(clients))

        ds = MongoMultiClientIndexModelDemo.find({'name':d.name})
        self.assertEqual(1, len(ds))
        for k in ['name', 'loc', 'daxue', 'xiaoqu', 'xueyuan', 'gender']:
            print '%s: %s|%s' % (k, getattr(d, k), getattr(ds[0], k))
            self.assertEqual(getattr(d, k), getattr(ds[0], k))

        ds = MongoMultiClientIndexModelDemo.find({'daxue':d.daxue, 'xiaoqu':d.xiaoqu, 'xueyuan':d.xueyuan})
        self.assertEqual(1, len(ds))
        for k in ['name', 'loc', 'daxue', 'xiaoqu', 'xueyuan', 'gender']:
            print '%s: %s|%s' % (k, getattr(d, k), getattr(ds[0], k))
            self.assertEqual(getattr(d, k), getattr(ds[0], k))

    def test_find_page(self):
        # 测试分页
        gender = '1'
        page_size = 10
        next_page = 1
        while True:
            ds = MongoMultiClientIndexModelDemo.find({'gender':gender}, limit=page_size, skip=page_size*(next_page-1))
            if len(ds) ==  0:
                break
            print 'find page: %s docs' % len(ds)
            for dd in ds:
                self.assertEqual(gender, dd.gender)
            next_page = next_page + 1


    def test_nearby(self):
        gender = '1'
        # loc = [random.randint(-170,170), random.randint(-80,80)]
        loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)]
        ds = MongoMultiClientIndexModelDemo.nearby(loc, criteria={'gender': gender}, with_distance=True)
        for d in ds:
            print d.to_dict(extra_keys=['distance'])
            self.assertEqual(d.gender, gender)
            self.assertTrue(d.distance is not None)

        min_distance = 40000
        max_distance = 60000 
        ds = MongoMultiClientIndexModelDemo.nearby(loc, criteria={'gender': gender}, with_distance=True, min_distance=min_distance, max_distance=max_distance)
        for d in ds:
            print d.to_dict(extra_keys=['distance'])
            self.assertEqual(d.gender, gender)
            self.assertTrue(d.distance is not None)
            self.assertTrue(d.distance >= min_distance and d.distance <= max_distance)


    def prepare_data(self):
        startms = int(time.time()*1000)
        for i in xrange(100000):
            mid = str(int(time.time()*1000))
            d = MongoMultiClientIndexModelDemo(mid=mid)
            d.name = str('name%s%s' % (time.time(), random.randint(1,100000)))
            d.loc = [117+(random.randint(10000,90000)/100000.0), 36+(random.randint(10000,90000)/100000.0)]
            d.daxue = str(random.randint(100,200))
            d.xiaoqu = str(random.randint(10,20))
            d.xueyuan = str(random.randint(1000,2000))
            d.gender = str(random.randint(1,2))
            count = d.save()
            self.assertEqual(count, len(clients))

            endms = int(time.time()*1000)
            if i%100 == 0:
                print ('avg cost: %s, total cost: %s' % ((endms-startms)/(i+1), (endms-startms)))
        print('avg cost: %s, total cost: %s' % ((endms-startms)/(i+1), (endms-startms)))




