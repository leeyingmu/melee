# -*- coding: utf-8 -*-

'''
翻页器接口协议定义，用于统一所有需要翻页逻辑的类的翻页操作
翻页协议不涉及存储，区别于同步器协议。
'''

import simplejson as json
import time

class PagerCursor(object):
    '''翻页器游标定义'''
    
    def __init__(self, cursorid, **kwargs):
        self.cursorid = cursorid
        self.extra = kwargs

    def __str__(self):
        return json.dumps({'cursorid': self.cursorid, 'extra': self.extra})

    @classmethod
    def load(cls, value):
        if not value: return None
        d = json.loads(value)
        return cls(d.get('cursorid'), **d.get('extra', {}))

    @classmethod
    def gen_cursorid(cls, timestamp=None, counter=None):
        '''
        generate a new cursorid
        cursorid is a 64-bits Integer and a new cursorid is always bigger than old ones.
        :param timestamp: `integer` million seconds
        :param counter: `integer` timestamp 参数范围内的增长计数器，默认为0
        '''
        timestamp = timestamp or int(time.time()*1000)
        counter = counter or 0
        return (timestamp<<22) + (counter<<12)


class Pager(object):
    '''翻页器实现'''

    '''是倒序查询还是正序查询'''
    __desc__ = True
    
    def page(cls, cursor, limit=10, **kwargs):
        '''按页查询
        :param cursor: `PagerCursor` 
        Return (items, next_cursor), items is a list, next_cursor is an object of PagerCursor
        '''
        raise RuntimeError('not implemented method error, you should use specific sub-class of Pager')





