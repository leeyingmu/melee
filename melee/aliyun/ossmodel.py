# -*- coding: utf-8 -*-

import sys, traceback
from oss import oss_xml_handler
from oss.oss_api import *

from ..core.env import logger

def format_key(key):
    if not key:
        return key
    parts = key.split('/')
    parts = [p for p in parts if p]
    return '/'.join(parts)

class OSSBucket(object):
    '''
    all bucket operations of the aliyun oss bucket
    '''

    def __init__(self, name, regionid=None, access_key_id=None, access_key_secret=None, acl=None):
        self.name = name
        self.acl = acl or 'private'
        self.client = OssAPI('oss-%s' % regionid, access_key_id, access_key_secret)
        pass

    
    @classmethod
    def list_all_buckets(cls, prefix=None):
        pass

    def list_objects(self, prefix=None):
        pass



class OSSObject(object):
    '''
    all Object operations of the aliyun oss Object
    '''

    def __init__(self, bucket, key, regionid=None, access_key_id=None, access_key_secret=None):
        self.bucket = bucket
        self.key = format_key(key)
        self.client = OssAPI('oss-%s' % regionid, access_key_id, access_key_secret)

    @property
    def data(self):
        if getattr(self, '_data', None) is None:
            try:
                rs = self.client.get_object(self.bucket, self.key)
                if rs.status != 200:
                    raise RuntimeError('failed to get oss file %s/%s, %s, %s' % (self.bucket, self.key, rs.status, rs.read()))
                self._data = rs.read()
            except:
                logger.error('EXCEPTION', sys.exc_info()[1])
                logger.error('TRACEBACK', traceback.format_exc())
                self._data = ''
        return self._data

    def refresh(self):
        self._data = None


    def update(self, data):

        # 清空原数据
        self.refresh()







