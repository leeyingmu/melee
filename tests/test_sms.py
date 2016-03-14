# -*- coding: utf-8 -*-

import unittest, random, json
from melee.core.env import config
from melee.core.sms import SMSPool, CCPSMS, NeteaseSMS, smspool

class Test(unittest.TestCase):

    def test_netease_sms(self):
        phone = '18600463306'
        template_id = '8197'
        kwargs = {'baseurl': 'https://api.netease.im', 'appkey': '9a1be2bcfe063aab5b41cff4e7a6bf9c', 'appsecret': '0809de49bd1d'}
        sms = NeteaseSMS(**kwargs)
        sms.send_sms_verifycode(phone, template_id=template_id, expire=300)

    def test_ccp_sms(self):
        phone = '18600463306'
        template_id = '62769'
        kwargs = {'baseurl': 'https://app.cloopen.com:8883/2013-12-26', 'account_sid': '8a48b5514f4fc588014f5db4b7de1405', 'account_token': 'd7924d01ff174aed9261c0fa5864de69', 'app_id': 'aaf98f89524954cc015253d7658f13dc', 'app_token': '2c0bca31a87a34278a9b15e219f483ad'}
        sms = CCPSMS(**kwargs)
        sms.send_sms_verifycode(phone, template_id=template_id, expire=300)

    def test_smspool(self):
        phone = '18600463306'
        template_id = '62769'
        smspool.send_sms_verifycode(phone, template_id=template_id, expire=500)
