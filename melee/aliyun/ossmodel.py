# -*- coding: utf-8 -*-

import sys, traceback, time, urlparse, hashlib
from ..core import utils
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
    已经废弃
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
    已经废弃
    '''

    def __init__(self, bucket, key, regionid=None, access_key_id=None, access_key_secret=None):
        self.bucket = bucket
        self.key = format_key(key)
        self.client = OssAPI('oss-%s' % regionid, access_key_id, access_key_secret)

    @property
    def data(self):
        return self.get_data()

    def get_data(self, refresh=False):
        if refresh or getattr(self, '_data', None) is None:
            rs = self.client.get_object(self.bucket, self.key)
            if rs.status != 200:
                raise RuntimeError('failed to get oss file %s/%s, %s, %s' % (self.bucket, self.key, rs.status, rs.read()))
            self._data = rs.read()
        return self._data

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

    @property
    def data(self): return self.get()

    def get(self, refresh=False):
        if refresh or not getattr(self, '_data', None):
            d = None
            try: 
                d = self.bucket.get_object(self.key).read()
            except:
                logger.error('oss object load failed', self.bucket_name, self.key)
                logger.error('EXCEPTION', exc_info=sys.exc_info())
                logger.error('TRACEBACK', traceback.format_exc())
            if d: 
                self._data = d
        return self._data

    def put_object(self, data, **kwargs):
        '''上传文件到该object
        :param data: 待上传的内容。
        :type data: bytes，str或file-like object
        其它参数参考oss2.Bucket的put_obejct参数
        '''
        self.bucket.put_object(self.key, data, **kwargs)
        logger.debug('put_object', self.key, kwargs)


class OSS2ConfigObject(BaseOSS2Object):
    pass


# class OSS2ImgObject(BaseOSS2Object):
#     '''oss2 图片处理'''

#     def __init__(self, key, bucket_name, endpoint, access_key_id, access_key_secret, urldomain=None):
#         '''
#         :param urldomain: `string` 当前bucket绑定的域名或者CDN域名
#         '''
#         super(OSS2ImgObject, self).__init__(key, bucket_name, endpoint, access_key_id, access_key_secret)
#         self.urldomain = urldomain
#         self.img_endpoint = '%s-%s' % ('img', self.endpoint[3:])

    # def url(self, style=None, action=None, picformat=None):
    #     '''获取该图片的访问地址
    #     :param style: `string` 在oss控制台图片服务中定义的样式快捷方式
    #     :param action: `string` oss 图片服务的处理动作，格式参考oss图片处理关键词说明： https://help.aliyun.com/document_detail/oss/oss-img-guide/access/keyword.html?spm=5176.docoss/oss-img-guide/access/url.6.439.C9JQva
    #     :param picformat: `string` 将图片转换成什么格式
    #     其中style参数与action、picformat不能同时使用，style本身就是action和picformat的快捷方式
    #     Return 生成的图片地址
    #     '''
    #     if not self.urldomain: url = 'http://%s.%s/%s' % (self.bucket_name, self.img_endpoint, self.key)
    #     else: url = 'http://%s/%s' % (self.urldomain, self.key)
    #     if style: url = '%s@!%s' % (url, style)
    #     if action: url = '%s@%s' % (url, action)
    #     if picformat: url = '%s@%s' % (url, picformat)
    #     return url



class OSS2ImgObject(BaseOSS2Object):
    '''用于对数据型图片的使用操作，该类定义的图片都存在于固定的目录下
       请确保该bucket开通图片处理服务
    '''
    __base_path__ = None
    __bucket_name__ = None
    __endpoint__ = None
    __access_key_id__ = None
    __access_key_secret__ = None
    __urldomain__ = None
    __action_separator__ = '@'
    __style_separator__ = '@!'

    def __init__(self, path=None, filename=None, rename=False):
        self.path = utils.format_path(path) if path else None
        self.filename = self.new_filename(filename=filename) if rename or not filename else filename
        super(OSS2ImgObject, self).__init__(utils.format_path(self.__base_path__, self.path, self.filename), self.__bucket_name__, self.__endpoint__, self.__access_key_id__, self.__access_key_secret__)

    @classmethod
    def new_filename(cls, filename=None):
        imgformat = filename.split('.')[1] if filename and len(filename.split('.')) > 1 else None
        filename = '%s_%s' % (int(time.time()*1000), utils.uuid1())
        return '%s.%s' % (filename, imgformat) if imgformat else filename

    def url(self, style=None, action=None, picformat=None):
        '''获取该图片的访问地址
        :param style: `string` 在oss控制台图片服务中定义的样式快捷方式
        :param action: `string` oss 图片服务的处理动作，格式参考oss图片处理关键词说明： https://help.aliyun.com/document_detail/oss/oss-img-guide/access/keyword.html?spm=5176.docoss/oss-img-guide/access/url.6.439.C9JQva
        :param picformat: `string` 将图片转换成什么格式
        其中style参数与action、picformat不能同时使用，style本身就是action和picformat的快捷方式
        Return 生成的图片地址
        '''
        if not self.__urldomain__: url = 'http://%s.%s/%s' % (self.__bucket_name__, self.__endpoint__, self.key)
        else: url = 'http://%s/%s' % (self.__urldomain__, self.key)

        if style: url = '%s@!%s' % (url, style)
        if action: url = '%s@%s' % (url, action)
        if picformat: url = '%s@%s' % (url, picformat)
        return url

    @classmethod
    def url_parse(cls, url):
        '''将一个url解析成对象'''
        p = urlparse.urlparse(url)
        path = utils.format_path(p.path.split(cls.__action_separator__)[0])
        print path
        path = path.replace(cls.__base_path__, '', 1)
        print path
        parts = utils.format_path(path).split('/')
        print parts
        path = utils.format_path(*parts[0:len(parts)-1]) if len(parts) > 1 else None
        filename = parts[-1]
        return cls(path=path, filename=filename)

    @classmethod
    def upload(cls, data, path=None, filename=None, **kwargs):
        '''上传一个图片
        :param kwargs: 参数参考oss bucket put_object 方法
        '''
        filename = filename or cls.new_filename()
        f = cls(path=path, filename=filename, rename=False)
        f.put_object(data, **kwargs)
        logger.debug('imgobject upload', cls.__base_path__, f.path, f.filename, kwargs)
        return f

























