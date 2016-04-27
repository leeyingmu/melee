# -*- coding: utf-8 -*-
import hashlib, copy, time, requests, urllib2 as urllib
from ..core import utils, json
from ..webhttp.exceptions import BadRequest
from ..core.env import config, logging
from ..core.signalslot import BaseSignal, signal

logger = logging.getLogger('CALLBACKPAY')

class CallbackPaySignal(BaseSignal):
    # 新提交订单
    beecloud = signal('callbackpay.beecloud')

__signal__ = CallbackPaySignal()

class _BasePay(object):
    
    __attrs__ = []

    def __init__(self, **kwargs):
        self._data = copy.deepcopy(kwargs)

    def __getattr__(self, name):
        if name in self.__attrs__:
            return self._data.get(name)
        else:
            return super(_BasePay, self).__getattr__(name)

    def to_dict(self):
        return copy.deepcopy(self._data)

    @classmethod
    def verify_request(cls, g):
        '''验证请求是否合法，并返回该pay的对象实例'''
        pass

    def process(self):
        '''执行支付、退款操作'''
        pass


class BeeCloudPay(_BasePay):

    __beecloud_config__ = { c.get('appid'): c for c in config.callbackpays.get('beecloud')}
    __beecloud_appid__ = __beecloud_config__.get(config.appids[0]).get('appID')
    __beecloud_appsecret__ = __beecloud_config__.get(config.appids[0]).get('appSecret')
    __melee_secret__ = __beecloud_config__.get(config.appids[0]).get('meleeSecret')

    __attrs__ = [
        'sign', 'timestamp', 'channel_type', 'sub_channel_type', 'transaction_type', 'transaction_id', 'transaction_fee', 'optional'
    ]

    @classmethod
    def verify_request(cls, g):
        if cls.__melee_secret__ != g.melee_secret:
            raise BadRequest(description='secret config error %s' % g.appid)

        kwargs = {k: g.jsondata.get(k) for k in cls.__attrs__ if g.jsondata.get(k) is not None}
        if len(kwargs) != len(cls.__attrs__):
            raise BadRequest(description='invalid parameters')

        timestamp = g.jsondata.get('timestamp')
        sign = g.jsondata.get('sign').lower()
        thissign = hashlib.md5(cls.__beecloud_appid__ + cls.__beecloud_appsecret__ + str(timestamp)).hexdigest().lower()
        if thissign != sign:
            raise BadRequest(description='sign error')
        return cls(**kwargs)

    def process(self):
        '''发送signal'''
        zhifu_mid = self.optional.get('zhifu_mid')
        billtype = self.optional.get('billtype', 'order')
        if len(__signal__.beecloud.receivers) < 1:
            raise RuntimeError('not receivers for %s' % __signal__.beecloud.name)
        __signal__.send(__signal__.beecloud, self, billtype=billtype, zhifu_mid=zhifu_mid, catch_except=False)
        logger.info('processed', __signal__.beecloud, '%s receivers' % len(__signal__.beecloud.receivers))


    # def process(self):
    #     if str(self.transaction_type).upper() not in  ['PAY', 'REFUND']:
    #         raise BadRequest(description='not supported transaction_type')
    #     if str(self.transaction_type).upper() == 'PAY':
    #         if self.order.status < Order2Status.paid:
    #             zhifu_mid = self.optional.get('zhifu_mid')
    #             if not zhifu_mid:
    #                 raise BadRequest(description='invalid optional parameters')
    #             self.order.transaction_id = self.transaction_id
    #             self.order.zhifu_mid = zhifu_mid
    #             self.order.zhifu_channel = self.sub_channel_type
    #             self.order.save()
    #             self.order.update_status(Order2Status.paid)
    #             self.order.append_status_detail(operator=zhifu_mid, desc='支付成功，等待商家确认!')
    #             logger.info('beecloud PAY success', self.to_dict())
    #         else:
    #             logger.info('beecloud PAY duplicated request', self.order.orderid, self.to_dict())
    #         return True

    #     logger.error('beecloud not supported transaction_type', self.transaction_type)
    #     return False


    @classmethod
    def query_zhifu_count(cls, success=True, starttime=None, endtime=None):
        timestamp = int(time.time()*1000)
        para = {
            'app_id': cls.__beecloud_appid__,
            'timestamp': timestamp,
            'app_sign': utils.hash('md5', '%s%s%s' % (cls.__beecloud_appid__, timestamp, cls.__beecloud_appsecret__)),
            'spay_result': success
        }
        if starttime: para['start_time'] = starttime
        if endtime: para['end_time'] = endtime

        url = '%s?para=%s' % ('https://apidynamic.beecloud.cn/2/rest/bills/count', urllib.quote(json.dumps(para)))
        logger.debug('beecloud query', url)

        rs = requests.get(url)
        if rs.status_code != 200:
            raise RuntimeError('filed to query beelcoud')
        data = json.loads(rs.text)
        logger.info('beecloud query zhifu count', data)
        return data.get('count') or 0











