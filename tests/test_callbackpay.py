# -*- coding: utf-8 -*-

import copy, time, unittest, hashlib, hmac, random
from melee.core import json, utils
from melee.core.signalslot import signalslot
from melee.webhttp import helpers
from server import app, config

from melee.callbacks.callbackpay_view import blueprint as callbackpay_view_blueprint
app.mount([callbackpay_view_blueprint], prefix={callbackpay_view_blueprint.name: '/%s' % config.servicename})

appid = '2'
appID = 'd887281a-ae69-4d93-8f36-527fea8c3d81'
appSecret = '0162e9e7-5918-45bd-83f3-ab775d592c1e'
meleeSecret = 'SlEQDSO8RlphzXPC'

@signalslot('callbackpay.beecloud')
def on_callbackpay_beecloud(pay, billtype, zhifu_mid):
    print '--------------------------------'
    print 'in on_callbackpay_beecloud'
    print pay
    print billtype
    print zhifu_mid 
    # raise RuntimeError('test error')
    print '--------------------------------'

class Test(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_beecloud(self):
        url = '/%s/callbackpay/beecloud/%s/%s' % (config.servicename, appid, meleeSecret)
        timestamp = str(int(time.time()*1000))
        data = {
            'app_id': appID,
            'app_secret': appSecret,
            'timestamp': timestamp,
            'sign': utils.hash('md5', '%s%s%s'%(appID, appSecret, timestamp)),
            'channel_type': 'WX',
            'transaction_type': 'PAY',
            'sub_channel_type': 'test',
            'transaction_id': str(time.time()),
            'transaction_fee': 123,
            'optional': {'zhifu_mid': 'testmid'},
            'trade_success': True,
            'message_detail': {}
        }
        code, rs = helpers.send_test_str_request(self.app, url, data=json.dumps(data))
        self.assertEqual(200, code)
        self.assertEqual('success', rs)


