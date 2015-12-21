# -*- coding: utf-8 -*-

import datetime, time, sys, traceback, copy, random, math
reload(sys)
sys.setdefaultencoding('utf8')

from melee.core import utils
from melee.core.env import config, logging
from pymongo import IndexModel


class BaseMongoMultiClientIndexModel(object):
    '''
    该模型是以多机并列mongo实例构建的高可用查询模型。
    将无法索引的数据，如redis用户数据，通过该模型多机写，单机查的方式，实现高可用查询索引。
    '''
    __db_name__ = None
    __collection_name__ = None

    __attrs__ = []

    '''主键索引'''
    __keys__ = []

    '''pymongo.IndexModel 实例数组，用于初始化创建索引'''
    __indexes__ = []

    # 所有实例连接中的db对象
    __dbs__ = []
    # 所有实例连接中的collection对象
    __collections__ = []

    logger = logging.getLogger('mongodb.%s.%s' % (__db_name__, __collection_name__)) if __db_name__ and __collection_name__ else logging.getLogger('mongodb')

    @classmethod
    def create_index(cls):
        cls.initdb()
        index_names = [i.document.get('name') for i in cls.__indexes__]
        for c in cls.__collections__:
            c.create_indexes(cls.__indexes__)
            cls.logger.info('create_indexs', 'in client: %s' % cls.__collections__.index(c), index_names)

    @classmethod
    def initdb(cls):
        # 所有实例连接中的db对象
        if not cls.__dbs__:
            cls.__dbs__ = [c[cls.__db_name__] for c in config.mongodb_clients] if cls.__db_name__ else []
        # 所有实例连接中的collection对象
        if not cls.__collections__:
            cls.__collections__ = [db[cls.__collection_name__] for db in cls.__dbs__] if cls.__db_name__ and cls.__collection_name__ else []


    def __init__(self, doc=None, **kwargs):
        self.initdb()
        for k in ['_id', 'ut']:
            if k in self.__attrs__:
                continue
            self.__attrs__.append(k)

        self._doc = doc or {}
        if not self._doc:
            self._doc = kwargs
            self._doc = self.random_collection().find_one(self.key) or kwargs or {}
        self._old = copy.deepcopy(self._doc)
        self._changed = {}
    
    @property
    def key(self): return {k:v for k,v in self._doc.iteritems() if k in self.__keys__}
    @property
    def exists(self): return self._doc and '_id' in self._doc
   
    @classmethod
    def random_db(self): return self.__dbs__[random.randint(0, len(self.__dbs__)-1)] if len(self.__dbs__) else None
    @classmethod
    def random_collection(self): return self.__collections__[random.randint(0, len(self.__collections__)-1)] if len(self.__collections__) else None

    def __setattr__(self, name, value):
        if name not in self.__attrs__:
            super(BaseMongoMultiClientIndexModel, self).__setattr__(name, value)
        else:
            self._doc[name] = value
            self._changed[name] = value

    def __getattr__(self, name):
        if name not in self.__attrs__:
            return super(BaseMongoMultiClientIndexModel, self).__getattr__(name)
        return self._doc.get(name)

    def to_dict(self, extra_keys=None): 
        d = copy.deepcopy(self._doc)
        for k in extra_keys or []:
            v = getattr(self, k)
            if isinstance(v, list) or isinstance(v, dict):
                v = copy.deepcopy(v)
            d[k] = v
        return d

    def save(self, upsert=True):
        '''保存或者更新一条文档，循环保存到多机中，忽略其中单机保存出现的错误'''
        count = 0
        if not self.key:
            self.logger.error('key not specified', self._doc)
            raise RuntimeError('key not specified error')
        if not self._changed:
            self.logger.warn('nothing changed', self._doc, self._changed)
            return count
        self.ut = int(time.time()*1000)
        startms = int(time.time()*1000)
        for c in self.__collections__:
            # 保存到多机
            try: 
                rs = c.update_one(self.key, {'$set': self._doc}, upsert=upsert)
                count += 1
                self.logger.info('multi instance update success', self.__collections__.index(c), self.key, 'old', self._old, 'changed', self._changed, 'new', self._doc, 'cost avg:%sms'%((int(time.time()*1000)-startms)/count))
            except:
                self.logger.error('multi instance update ERROR', self.__collections__.index(c), self.key, 'old', self._old, 'changed', self._changed, 'new', self._doc)
                self.logger.error('EXCEPTION', exc_info=sys.exc_info())
                self.logger.error('TRACEBACK', traceback.format_exc())
        if count != len(self.__collections__):
            # 多机写结果不一致
            self.logger.error('multi instance update CONSISTENT ERROR', self.key, 'old', self._old, 'changed', self._changed, 'new', self._doc, count)
        # 清空修改记录
        self._changed = {}
        return count


    def replace(self, replace):
        '''替换一条文档，循环保存到多机中，忽略其中单机保存出现的错误'''
        count = 0
        if not replace: return
        if not self.key:
            self.logger.error('key not specified', self._doc)
            raise RuntimeError('key not specified error')
        
        # 保证文档的key必须是完整的
        replace.update(self.key)

        replace['ut'] = int(time.time()*1000)
        startms = int(time.time()*1000)
        for c in self.__collections__:
            # 替换多机上的内容
            try:
                rs = c.replace_one(self.key, replace)
                count += 1
                self.logger.info('multi instance replace success', self.__collections__.index(c), self.key, 'old', self._doc, 'new', replace, 'cost avg:%sms'%((int(time.time()*1000)-startms)/count))
            except:
                self.logger.error('multi instance replace ERROR', self.__collections__.index(c), self.key, 'old', self._doc, 'new', replace)
                self.logger.error('EXCEPTION', exc_info=sys.exc_info())
                self.logger.error('TRACEBACK', traceback.format_exc())          
        if count != len(self.__collections__):
            # 多机写结果不一致
            self.logger.error('multi instance replace CONSISTENT ERROR', self.key, 'old', self._doc, 'new', replace, count)
        return count


    @classmethod
    def find(cls, *args, **kwargs):
        '''参数同pymongo.collection.Collection find 方法'''
        startms = int(time.time()*1000)
        docs = cls.random_collection().find(*args, **kwargs)
        items = [ cls(doc=doc) for doc in docs]
        cls.logger.debug('find', args, kwargs, len(items), 'cost:%sms'%(int(time.time()*1000)-startms))
        return items

    @classmethod
    def nearby(cls, loc, min_distance=None, max_distance=None, criteria=None, limit=30, skip=0, with_distance=False, **kwargs):
        '''根据 "2dsphere" 索引查找附近数据
           :param loc: 经纬度数据 [经度,纬度] 数字类型
           :param min_distance: 最小搜索距离，单位米
           :param max_distance: 最大搜索距离，单位米
           :param criteria: 其它过滤条件字典，格式参考mongo的find命令或者pymongo.collection.Collection的find函数的filter参数
           :param with_distance: 是否计算距离，单位时米，返回单位为米，整数
        '''
        if not loc or not isinstance(loc, list) or not len(loc)==2:
            raise RuntimeError('loc error, you must provide a valid loc=[longitude,latitude] with number type')
        criteria = criteria or {}
        criteria.update({
            'loc': {
                '$nearSphere': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': loc
                    }
                    # '$geometry': loc
                }
            }
        })
        if min_distance and min_distance > 0: criteria['loc']['$nearSphere']['$minDistance'] = min_distance
        if max_distance and max_distance > 0: criteria['loc']['$nearSphere']['$maxDistance'] = max_distance

        items = cls.find(criteria, limit=limit, skip=skip, **kwargs)
        if with_distance:
            for item in items:
                item.distance = int(cls.distance(loc, item.loc))
        return items

    @classmethod
    def distance(cls, p1, p2):
        '''计算两点间距离，单位为米，p1和p2是两个经度度表示的点，格式都为数字数组[经度,纬度]'''
        R = 6371000
        c = math.sin(p1[1])*math.sin(p2[1])*math.cos(p1[0]-p2[0]) + math.cos(p1[1])*math.cos(p2[1])
        return R*math.acos(c)*math.pi/180

















