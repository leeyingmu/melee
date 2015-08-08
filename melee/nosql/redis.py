# -*- coding: utf-8 -*-

import redis, copy
from ..core import json



class BaseRedisModel(object):

    __keyprefix__ = None


class RedisHashModel(BaseRedisModel):
    
    # 不让用户随便看到的属性
    __notvisible_attrs__ = []
    # 不让别人看到的属性
    __notpersona_attrs__ = []

    @property
    def key(self):
        # implemented by the specific subclass
        raise RuntimeError('not implemented operation')

    @property
    def client(self):
         # implemented by the specific subclass
         # the redis connection client
        raise RuntimeError('not implemented operation')

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

    def __getattr__(self, name):
        # 所有没有实际定义的属性，都会从此处获取
        if name in ['_origindata']:
            return super(BaseObject, self).__getattr__(name)
        return self._origindata.get(name) or None

    @property
    def exists(self):
        return self._origindata is not None and len(self._origindata) > 0

    def update(self, update_data):
        if not update_data:
            return
        self.client.hmset(self.key, update_data)
        self.clear_cache()

    def clear_cache(self):
        self.__origindata = None


    def apiinfo(self, for_persona=False):
        info = self.data
        for k in self.__notvisible_attrs__:
            info.pop(k, None)
        if for_persona:
            for k in self.__notpersona_attrs__:
                info.pop(k, None)
        return info

