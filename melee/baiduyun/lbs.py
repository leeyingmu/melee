# -*- coding: utf-8 -*-

import requests

from ..core import json


class LBSTable(object):

    __tablename__ = None
    __geotype__ = 1

    __columns__ = [
        # {
        #     'name': '中文名别太长，在百度云控制台标注时展示不全，不要超过四个汉字',
        #     'key': '字段英文名',
        #     'type': 1/2/3, #1:int64, 2:double, 3:string
        #     # 其它字段参考百度lbs云column创建接口
        # },
        # {}
    ]

    def __init__(self, ak=None, **kwargs):
        self.ak = ak
        self.id = kwargs.get('id')
        self.geotype = kwargs.get('geotype')


    @classmethod
    def _send_request(cls, url, params=None, post=True):
        if post: rs = requests.post(url, data=params)
        else: rs = requests.get(url, params=params)
        if rs.status_code != 200:
            raise RuntimeError('baiduyun lbs network error: %s' % rs.status_code)
        data = json.loads(rs.text)
        if not data.get('status') in [0]:
            raise RuntimeError('baiduyun lbs response error: %s' % rs.text)
        return data


    @classmethod
    def get_table(cls, ak):
        if not cls.__tablename__:
            raise RuntimeError('not supported operations for table %s which is not defined' % cls.__tablename__)
        url = 'http://api.map.baidu.com/geodata/v3/geotable/list'
        data = cls._send_request(url, params={'ak':ak, 'name': cls.__tablename__}, post=False)
        if data.get('size') == 1:
            kwargs = data.get('geotables')[0]
            return cls(ak=ak, **kwargs)
        # 根据name查询到不止一个table
        raise RuntimeError('baiduyun lbs get table error, not only one: %s' % json.dumps(data))


    @classmethod
    def init_schema(cls, ak):
        t = cls.get_table(ak)
        columns = t.columns

        for c in cls.__columns__ or []:
            if c.get('key') in columns:
                continue
            t._create_column(**c)
        return True

    @property
    def columns(self):
        url = 'http://api.map.baidu.com/geodata/v3/column/list'
        data = self._send_request(url, params={'ak': self.ak, 'geotable_id': self.id}, post=False)
        return { c.get('key'):c for c in data.get('columns') or []}


    def _create_column(self, **kwargs):
        '''
        kwargs referenced to the api: http://api.map.baidu.com/geodata/v3/column/create
        '''
        url = 'http://api.map.baidu.com/geodata/v3/column/create'
        kwargs['geotable_id'] = self.id
        kwargs['ak'] = self.ak
        data = self._send_request(url, params=kwargs)
        # 0:成功, 2001:列key重复
        return True


    def query_nearby(self, location, **kwargs):
        '''
        检索指定坐标附近
        参数参考百度lbs云“云检索api”
        '''
        url = 'http://api.map.baidu.com/geosearch/v3/nearby'
        kwargs['location'] = '%s,%s' % (location[0], location[1]) if isinstance(location, list) else location
        kwargs['ak'] = self.ak
        kwargs['geotable_id'] = self.id
        data = self._send_request(url, params=kwargs, post=False)
        return data.get('contents')


    def query_local(self, region, **kwargs):
        '''
        检索指定"市/区"内
        参数参考百度lbs云“云检索api”
        '''
        url = 'http://api.map.baidu.com/geosearch/v3/local'
        kwargs['region'] = region  
        kwargs['ak'] = self.ak
        kwargs['geotable_id'] = self.id
        data = self._send_request(url, params=kwargs, post=False)
        return data.get('contents')

    def query_bound(self, bounds):
        '''
        检索指定矩形区域内
        参数参考百度lbs云“云检索api”
        '''
        url = 'http://api.map.baidu.com/geosearch/v3/bound'
        kwargs['bounds'] = bounds  
        kwargs['ak'] = self.ak
        kwargs['geotable_id'] = self.id
        data = self._send_request(url, params=kwargs, post=False)
        return data.get('contents')


