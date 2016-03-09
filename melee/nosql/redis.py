# -*- coding: utf-8 -*-

import redis, copy
from ..core import json



class BaseRedisModel(object):

    __keyprefix__ = None

    @property
    def key(self):
        # implemented by the specific subclass
        raise RuntimeError('not implemented operation')

    @property
    def client(self):
         # implemented by the specific subclass
         # the redis connection client
        raise RuntimeError('not implemented operation')

    def execute(self, cmd, *args, **kwargs):
        '''代理执行redis命令'''
        m = getattr(self.client, cmd)
        if not callable(m):
            raise RuntimeError('not supported command %s' % cmd)
        return m(*args, **kwargs)


class RedisHashModel(BaseRedisModel):
    
    # 不让用户随便看到的属性
    __notvisible_attrs__ = []
    # 所有可修改字段，为空的话不限制
    __attrs__ = []

    @property
    def _origindata(self):
        # 延迟加载数据
        if not getattr(self, '__origindata', None):
            self.__origindata = self.client.hgetall(self.key) or {}
        return self.__origindata

    @property
    def data(self):
        # 用户自己查看自己的信息
        info = copy.deepcopy(self._origindata)
        # 去除所有不能随便看的重点属性
        for k in self.__notvisible_attrs__:
            info.pop(k, None)
        return info

    def apiinfo(self):
        '''已经废弃，在老的cshop和dshop中还在使用'''
        return self.to_dict()

    def to_dict(self, extra_keys=None, exclude_keys=None):
        '''数据转化为dict结构
        :param extra_keys: 除了存储中字段外，还需要从self对象中获取的属性数据。
        :param exclude_keys: 需要排除在外的属性数据。
        '''
        d = self.data
        for k in extra_keys or []:
            v = getattr(self, k)
            if isinstance(v, list) or isinstance(v, dict):
                v = copy.deepcopy(v)
            d[k] = v
        for k in exclude_keys or []:
            d.pop(k, None)
        return d

    def __getattr__(self, name):
        # 所有没有实际定义的属性，都会从此处获取
        if name in ['__origindata']:
            return super(RedisHashModel, self).__getattr__(name)
        return self._origindata.get(name) or None

    @property
    def exists(self):
        return self._origindata is not None and len(self._origindata) > 0

    def update(self, update_data=None, incr=None, expire=None):
        update_data = update_data or {}
        update_data = {k:v for k,v in update_data.iteritems() if not self.__attrs__ or k in self.__attrs__}
        incr = incr or {}
        incr = {k:v for k,v in incr.iteritems() if not self.__attrs__ or k in self.__attrs__}
        if update_data:
            self.client.hmset(self.key, update_data)
        if incr:
            for name, delta in incr.iteritems():
                self.client.hincrby(self.key, name, amount=delta)
        if expire:
            self.client.expire(self.key, expire)
        self.clear_cache()

    def remove(self, *keys):
        for k in keys or []:
            self.client.hdel(self.key, k)
        self.clear_cache()

    def delete(self):
        self.client.delete(self.key)

    def expire(self, expire):
        self.client.expire(self.key, expire)

    def clear_cache(self):
        self.__origindata = None


class RedisSetModel(BaseRedisModel):
    '''redis set 模型'''
    pass
    

class RedisSortedSetModel(BaseRedisModel):
    '''redis sorted set 模型'''
    
    @property
    def count(self):
        return int(self.client.zcard(self.key) or 0)

    def ismember(self, v):
        return self.client.zscore(self.key, v) is not None

    def all(self, desc=True, **kwargs):
        '''kwargs参数参考zrange和zrevrange函数'''
        if desc: return self.client.zrevrange(self.key, 0, -1, **kwargs)
        else: return self.client.zrange(self.key, 0, -1, **kwargs)

