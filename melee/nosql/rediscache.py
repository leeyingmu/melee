# -*- coding: utf-8 -*-

import redis, copy
from ..core import json
from ..core.env import config, logging

logger = logging.getLogger('rediscache')

class BaseRedisCacheModel(object):
    '''基于redis做cache的基类，单实例cache'''

    __keyprefix__ = None
    __bind__ = None
    __expries__ = None

    __write_cmds__ = []

    @property
    def key(self):
        # implemented by the specific subclass
        raise RuntimeError('not implemented operation')

    @property
    def client(self):
        # the redis cache connection client
        return config.redis_cache(self.__bind__)
    
    @property
    def exists(self):
        return self.client.exists(self.key)
        

    def redis_execute(self, cmd, *args, **kwargs):
        '''代理执行redis命令'''
        m = getattr(self.client, cmd)
        if not callable(m):
            raise RuntimeError('not supported command %s' % cmd)
        rs = m(*args, **kwargs)
        if cmd in self.__write_cmds__:
            self.expire()

        print '2222222222222'
        print type(args)
        print args
        logger.debug('[REDIS EXECUTE]', cmd, args, kwargs)
        return rs

    def delete(self):
        return self.redis_execute('delete', self.key)

    def expire(self):
        return self.redis_execute('expire', self.key, self.__expries__)

    def rename(self, newname):
        return self.redis_execute('rename', self.key, newname)


class BaseRedisSortedSetCacheModel(BaseRedisCacheModel):
    '''基于zset实现的cache基类'''

    __max_size__ = None
    __write_cmds__ = ['zadd', 'zrem', 'zincrby', 'zremrangebylex', 'zremrangebyrank', 'zremrangebyscore']

    __desc__ = True

    @property
    def max_size(self): return self.__max_size__

    def remove_overstep(self):
        '''删除超出范围的'''
        size = self.redis_execute('zcard', self.key)
        if size <= self.__max_size__:
            return 0
        index = (self.__max_size__, -1) if not self.__desc__ else (0, size-self.__max_size__-1)
        return self.redis_execute('zremrangebyrank', self.key, *index)

    def redis_execute(self, cmd, *args, **kwargs):
        rs = super(BaseRedisSortedSetCacheModel, self).redis_execute(cmd, *args, **kwargs)
        if cmd == 'zadd':
            self.remove_overstep()
        return rs

    













