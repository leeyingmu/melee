# -*- coding: utf-8 -*-

import sys, traceback, time
from ..core.env import logging
from oss import oss_xml_handler
from oss.oss_api import *

'''oss2'''
import oss2

logger = logging.getLogger('aliyun.oss')

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
        # if getattr(self, '_data', None) is None:
        #     rs = self.client.get_object(self.bucket, self.key)
        #     if rs.status != 200:
        #         raise RuntimeError('failed to get oss file %s/%s, %s, %s' % (self.bucket, self.key, rs.status, rs.read()))
        #     self._data = rs.read()
        # return self._data
        rs = self.client.get_object(self.bucket, self.key)
        if rs.status != 200:
            raise RuntimeError('failed to get oss file %s/%s, %s, %s' % (self.bucket, self.key, rs.status, rs.read()))
        return rs.read()

    def update(self, data):
        pass


class BaseOSS2Object(object):
    '''all object operations of aliyun OSS servers based oss2 sdk module'''
    def __init__(self, key, bucket_name, endpoint, access_key_id, access_key_secret):
        '''参数参考oss2相关api
        '''
        self.key = key
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

        #缓存数据，两级缓存作用是保证在刷新缓存时如果出现网络失败，不会清空之前的缓存
        #只有当__data1加载成功时，才会赋值给__data2
        self.__data1 = None #读取缓存
        self.__data2 = None #加载缓存

    @property
    def data(self): return self.get()

    def get(self):
        # if not getattr(self, '__data1', None):
        #     try: 
        #         self.__data1 = self.bucket.get_object(self.key).read()
        #     except:
        #         logger.errorZ('oss object load failed', self.bucket_name, self.key)
        #         logger.error('EXCEPTION', exc_info=sys.exc_info())
        #         logger.error('TRACEBACK', traceback.format_exc())
        #     if self.__data1: 
        #         self.__data2 = self.__data1
        # return self.__data2
        return self.bucket.get_object(self.key).read()



class OSS2ConfigObject(BaseOSS2Object):
    pass


class OSS2ImgObject(BaseOSS2Object):
    pass
 




