# -*- coding: utf-8 -*-

import yaml

class YamlConfig(dict):

    def __init__(self, config_file=None):
        if not config_file:
            return
        with open(config_file) as f:
            self.update(yaml.load(f) or {})

    @property
    def servicename(self):
        return self.get('main', {}).get('servicename') or 'template'

    @property
    def log(self):
        log = self.get('main', {}).get('log') or {}
        log['rootname'] = self.servicename
        return log

    def sigkey(self, sig_kv):
        return self.get('main', {}).get('request', {}).get('sigkeys', {}).get(sig_kv)

    @property
    def tasklets(self):
        return self.get('tasklets')

    @property
    def redis_keyprefix(self):
        return self.get('main', {}).get('redis', {}).get('key_prefix')

    @property
    def redis_main(self):
        return self.redis_shard(0)

    def redis_shard(self, shardingid):
        '''
        按照指定的分片用的数据shardingid，根据配置的分片阈值sharding_threshold进行分片
        '''
        if not getattr(self, '_redisintances', None):
            self._redisintances = []
            import urlparse, redis
            for uri in self.get('main', {}).get('redis', {}).get('instances') or []:
                p = urlparse.urlparse(uri)
                self._redisintances.append(redis.Redis(p.hostname, port=p.port))
        sharding_threshold = int(self.get('main', {}).get('redis', {}).get('sharding_threshold'))
        return self._redisintances[int(shardingid)/sharding_threshold] if self._redisintances else None

    @property
    def aliyun_key(self):
        keys = {
            'regionid': self.get('main').get('aliyun').get('regionid') or 'cn-hangzhou.aliyuncs.com',
            'access_key_id': self.get('main').get('aliyun').get('access_key_id'),
            'access_key_secret': self.get('main').get('aliyun').get('access_key_secret')
        }
        return keys

    @property
    def aliyun_oss(self):
        return self.get('main').get('aliyun').get('oss')

    @property
    def baiduyun_ak(self):
        return self.get('main').get('baiduyun').get('ak')

    





    
