# -*- coding: utf-8 -*-

import yaml
import copy

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
    def debugmode(self):
        return 'true' == str(self.get('main').get('debugmode')).lower()

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
                if p.username and p.password:
                    self._redisintances.append(redis.Redis(p.hostname, port=p.port, password='%s:%s'%(p.username, p.password)))
                else:
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

    def rds_url(self, index=0):
        return self.get('main').get('rds')[index]

    @property
    def ccp_client(self):
        ccp_config = copy.deepcopy(self.get('main').get('ccp'))
        from .sms import CCP
        baseurl = ccp_config.pop('baseurl')
        return CCP(baseurl, **ccp_config)

    @property
    def rds_pool_config(self):
        c = copy.deepcopy(self.get('main').get('rds', {}).get('pool_config', {}))
        c['pool_size'] = c.get('pool_size') or 10
        c['pool_timeout'] = c.get('pool_timeout') or 10
        c['pool_recycle'] = c.get('pool_recycle') or 300
        c['max_overflow'] = c.get('max_overflow') or 0
        c['commit_on_teardown'] = c.get('commit_on_teardown', True)
        if self.debugmode:
            c['echo'] = True
            c['echo_pool'] = True
        c = {'SQLALCHEMY_%s' % k.upper() : v for k,v in c.iteritems()}
        return c

    @property
    def rds_binds(self):
        return self.get('main').get('rds', {}).get('binds') or {}



    





    
