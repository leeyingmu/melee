# -*- coding: utf-8 -*-

import unittest, random, json

from melee.baiduyun.lbs import LBSTable

ak = 'toZrtVntXNkSjMxNYprKOVlz'

class TestTable(LBSTable):
    __tablename__ = 'hclz_cshops'
    __columns__ = [
        {'name': 'cid', 'key': 'cid', 'type':3, 'is_unique_field': 1, 'max_length': 32}
    ]

class Test(unittest.TestCase):

    def test_init_schema(self):
        TestTable.init_schema(ak)

    def test_query_nearby(self):
        t = TestTable.get_table(ak)
        location = [117.132932, 36.689060]

        # pois, page_index = t.lbsquery_nearby(location, radius=5000, sortby='distance:1', page_size=4, page_index=0)
        # for p in pois:
        #     print '-------------------------------------'
        #     print json.dumps(p)
        #     for k,v in p.iteritems():
        #         print '%s = %s' % (k, v)
        # print '------------------------------------------------------------------------------'
        # pois, page_index = t.lbsquery_local('济南市', sortby='distance:1', coord_type=3, location='117.132932,36.689060', page_size=4, page_index=0)
        # for p in pois:
        #     print '-------------------------------------'
        #     print json.dumps(p)
        #     for k,v in p.iteritems():
        #         print '%s = %s' % (k, v)

        print '------------------------------------------------------------------------------'
        pois, page_index = t.lbsquery_bound('117.104078,36.709402;117.179967,36.672128', sortby='distance:1', coord_type=3, page_size=4, page_index=0)
        for p in pois:
            print '-------------------------------------'
            print json.dumps(p)
            for k,v in p.iteritems():
                print '%s = %s' % (k, v)


    
            
