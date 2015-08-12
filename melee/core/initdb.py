# -*- coding: utf-8 -*-

'''
the standard interface for auto init db schemas of different types
'''

class InitDBModel(object):

    @classmethod
    def init_schema(cls):
        raise RuntimeError('not implemented operations')