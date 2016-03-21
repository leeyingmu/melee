# -*- coding: utf-8 -*-

import simplejson as json
import urllib2 as urllib
import datetime, time
import base64
import hashlib
import random
import utils
from .env import logging, config

logger = logging.getLogger('sms')

def format_time(dt):
    ''':param dt: instance of datetime.datetime'''
    return time.strftime('%Y%m%d%H%M%S', dt.timetuple())


class BaseSMS(object):
    '''短信服务基础接口'''

    @classmethod
    def send(cls, url, data=None, headers=None):
        headers = headers or {}
        req = urllib.Request(url)
        for k,v in headers.iteritems():
            req.add_header(k, v)
        if data:
            req.add_data(data)
        rs = urllib.urlopen(req)
        if rs.code != 200:
            raise RuntimeError('短信发送失败，请重试!')
        return rs

    def send_sms_verifycode(self, phone, template_id=None, verify_code=None, expire=60, length=4):
        '''发送短信验证码
        :param phone: `string` 接受验证码的手机号
        :param template_id: `string` 第三方短信服务模板id
        :param verify_code: `string` 验证码
        :param exprie: `int` 超时秒数
        :param lenght: `int` 验证码长度（几位数字）
        Return the verify_code which was sent really sent.
        '''
        verify_code = verify_code if verify_code else str(random.randint(1000, 9999))
        datas = [verify_code, str(expire/60)]
        self.send_sms(phone, template_id=template_id, datas=datas)
        return verify_code

    def send_sms(self, phone, template_id='1', datas=None):
        '''模板短信发送窗口'''
        raise RuntimeError('not implemented method')


class CCPSMS(BaseSMS):

    '''容联云通讯平台'''

    def __init__(self, baseurl=None, account_sid=None, account_token=None, app_id=None, app_token=None):
        self.baseurl = baseurl
        self.account_sid = account_sid
        self.account_token = account_token
        self.app_id = app_id
        self.app_token = app_token

    def send_sms(self, phone, template_id='1', datas=None):
        '''发送短信'''
        timestamp = format_time(datetime.datetime.now())
        sign = hashlib.md5('%s%s%s' % (self.account_sid, self.account_token, timestamp)).hexdigest().upper()
        url = '%s/Accounts/%s/SMS/TemplateSMS?sig=%s' % (self.baseurl, self.account_sid, sign)
        auth = base64.encodestring('%s:%s' % (self.account_sid, timestamp)).strip()

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': auth
        }
        data = {
            'to': phone,
            'appId': self.app_id,
            'templateId': template_id,
            'datas': datas
        }
        data = json.dumps(data)
        rs = self.send(url, data=data, headers=headers)
        rs_data = rs.read()
        logger.info('CCPSMS', 'send sms', headers, data, rs_data)
        rs_data = json.loads(rs_data)
        if rs_data.get('statusCode') != '000000':
            raise RuntimeError(rs_data.get('statusMsg'))
        return True


class NeteaseSMS(BaseSMS):
    '''网易云信sms'''
    def __init__(self, baseurl=None, appkey=None, appsecret=None):
        self.baseurl = baseurl
        self.appkey = appkey
        self.appsecret = appsecret

    def send_sms(self, phone, template_id='1', datas=None):
        url = '%s/sms/sendtemplate.action' % self.baseurl
        headers = {
            'AppKey': self.appkey,
            'Nonce': '%s%s' % (int(time.time()*1000), random.randint(100000, 999999)),
            'CurTime': '%s' % (int(time.time())),
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }
        headers['CheckSum'] = utils.hash('sha1', '%s%s%s' % (self.appsecret, headers.get('Nonce'), headers.get('CurTime')))
        data = 'templateid=%s&mobiles=["%s"]&params=%s' % (template_id, phone, json.dumps(datas))
        rs = self.send(url, data=data, headers=headers)
        rs_data = rs.read()
        logger.info('NeteaseSMS', 'send sms', headers, data, rs_data)
        rs_data = json.loads(rs_data)
        ##############
        #检查发送状态
        url = '%s/sms/querystatus.action' % self.baseurl
        headers = {
            'AppKey': self.appkey,
            'Nonce': '%s%s' % (int(time.time()*1000), random.randint(100000, 999999)),
            'CurTime': '%s' % (int(time.time())),
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }
        headers['CheckSum'] = utils.hash('sha1', '%s%s%s' % (self.appsecret, headers.get('Nonce'), headers.get('CurTime')))
        data = 'sendid=%s' % rs_data.get('obj')
        rs = self.send(url, data=data, headers=headers)
        logger.debug('NeteaseSMS', 'send sms check', data, rs.read())
        ##############
        if rs_data.get('code') != 200:
            raise RuntimeError(json.dumps(rs_data))
        return True


class SMSPool(BaseSMS):
    __mappings__ = {
        'neteasesms': NeteaseSMS,
        'yuntongxunsms': CCPSMS
    }

    def __init__(self, supported_sms=[]):
        self.supported_sms = supported_sms or []
        self.clients = []
        for c in config.sms_config:
            name = c.get('name')
            kwargs = c.get('kwargs')
            if supported_sms and name not in supported_sms:
                continue
            cls = self.__mappings__.get(name)
            self.clients.append(cls(**kwargs))

    def send_sms(self, phone, **kwargs):
        model = 10000
        index = random.randint(0, model*len(self.clients))/model
        return self.clients[index].send_sms(phone, **kwargs)

smspool = SMSPool()

