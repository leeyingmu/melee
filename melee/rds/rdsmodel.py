# -*- coding: utf-8 -*-

import datetime, time, sys, traceback
reload(sys)
sys.setdefaultencoding('utf8')

from melee.core import utils
from melee.webhttp import app

db = app.rdsdb
logger = app.logger

class RDSLibModel(object):
    '''业务逻辑层关系数据库模型，封装隐藏了对db.Model及其子类的操作'''

    # model 层模型类
    __model_cls__ = None
    # 所有可见属性定义
    __attrs__ = []
    # 主键
    __primary_key__ = []

    def __init__(self, model=None, **kwargs):
        '''
        :param model: the sqlalchemy model obj
        :param kwarys: must be the primary key
        '''
        if model:
            self.model = model
        else:
            primary_key = {k:v for k,v in kwargs.iteritems() if k in self.__primary_key__}
            query = db.session.query(self.__model_cls__)
            for k,v in primary_key.iteritems():
                query = query.filter(getattr(self.__model_cls__, k)==v)
            models = query.all()
            # 新数据，先构造
            self.model = models[0] if models else self.__model_cls__(ct=datetime.datetime.now(), ut=datetime.datetime.now(), **primary_key)
        
        self.exists = self.model._id is not None
        self.origin_data = self.to_dict() if self.exists else {}
        self.changed_data = {}

        for k,v in kwargs.iteritems():
            if k not in self.__primary_key__:
                setattr(self, k, v)

    def _mark_changed(self, name, value):
        if name in self.origin_data and self.origin_data.get(name)==value:
            return
        self.changed_data[name] = value
        

    def __getattr__(self, name):
        if name not in self.__attrs__:
            # 非数据库字段
            # 等价于 object.__getattr__(self, name)
            return super(RDSLibModel, self).__getattr__(name)
        return getattr(self.model, name)

    def __setattr__(self, name, value):
        if name not in self.__attrs__:
            # 非数据库字段
            # 等价于 object.__setattr__(self, name, value)
            super(RDSLibModel, self).__setattr__(name, value)
        else:
            setattr(self.model, name, value)
            self._mark_changed(name, value)

    @classmethod
    def get(cls, **kwargs):
        m = cls(**kwargs)
        return m if m.exists else None

    def incr(self, name, delta):
        '''对于数字类型的进行加减运算'''
        if name not in self.__attrs__:
            # 非数据类字段
            old = getattr(self, name) or 0
            super(RDSLibModel, self).__setattr__(name, old+delta)
        else:
            old = getattr(self, name)
            if old is not None:
                setattr(self.model, name, getattr(self.__model_cls__, name)+delta)
            else:
                old = 0
                setattr(self.model, name, old+delta)
            self._mark_changed(name, old+delta)

    def to_dict(self):
        '''将 rds 一条数据转化为 dict'''
        data = {k: getattr(self, k) for k in self.__attrs__}
        for k in ['ct', 'ut']:
            if k in self.__attrs__:
                data[k] = utils.format_time(getattr(self, k))
        return data

    def save(self):
        logger.debug('assets', 'update before', self.__class__.__name__, self.origin_data, self.changed_data, self.to_dict())
        if not self.changed_data:
            logger.info('assets', 'update', 'nothing changed', self.origin_data, self.changed_data)
            return
        try:
            db.session.add(self.model)
            db.session.commit()

            logger.info('assets', 'update', self.__class__.__name__, self.origin_data, self.changed_data)
        except:
            db.session.rollback()
            logger.error('assets', 'update failed', self.__class__.__name__, self.origin_data, self.changed_data)
            logger.error('EXCEPTION', exc_info=sys.exc_info())
            logger.error('TRACEBACK', traceback.format_exc())
            raise




