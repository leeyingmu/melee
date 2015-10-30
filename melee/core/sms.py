# -*- coding: utf-8 -*-

import simplejson as json
import urllib2 as urllib
import datetime, time
import base64
import hashlib
import random

def format_time(dt):
    ''':param dt: instance of datetime.datetime'''
    return time.strftime('%Y%m%d%H%M%S', dt.timetuple())


class CCP(object):

    '''容联云通讯平台'''

    def __init__(self, baseurl, account_sid=None, account_token=None, app_id=None, app_token=None):
        self.baseurl = baseurl
        self.account_sid = account_sid
        self.account_token = account_token
        self.app_id = app_id
        self.app_token = app_token


    def send_sms_verifycode(self, phone, template_id='1', verify_code=None, expire=60):
        '''
        发送短信验证码
        '''
        verify_code = verify_code if verify_code else str(random.randint(100000, 999999))
        datas = [verify_code, str(expire/60)]
        self.send_sms(phone, template_id=template_id, datas=datas)
        return verify_code


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
        req = urllib.Request(url)
        for k,v in headers.iteritems():
            req.add_header(k, v)
        req.add_data(json.dumps(data))
        rs = urllib.urlopen(req);
        if rs.code != 200:
            raise RuntimeError('短信验证码发送失败，请重试!')
        rs_data = rs.read()
        rs_data = json.loads(rs_data)
        if rs_data.get('statusCode') != '000000':
            raise RuntimeError(rs_data.get('statusMsg'))

        return True

