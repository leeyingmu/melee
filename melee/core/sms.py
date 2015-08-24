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
        print 


    def send_sms_verifycode(self, phone, template_id='1', verify_code=None, expire=60):
        '''
        发送短信验证码
        '''
        timestamp = format_time(datetime.datetime.now())
        sign = hashlib.md5('%s%s%s' % (self.account_sid, self.account_token, timestamp)).hexdigest().upper()
        url = '%s/Accounts/%s/SMS/TemplateSMS?sig=%s' % (self.baseurl, self.account_sid, sign)
        auth = base64.encodestring('%s:%s' % (self.account_sid, timestamp)).strip()

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': auth
        }

        verify_code = verify_code if verify_code else str(random.randint(100000, 999999))
        data = {
            'to': phone,
            'appId': self.app_id,
            'templateId': template_id,
            'datas': [verify_code, str(expire/60)]
        }

        req = urllib.Request(url)
        for k,v in headers.iteritems():
            req.add_header(k, v)
        req.add_data(json.dumps(data))
        rs = urllib.urlopen(req);
        if rs.code != 200:
            raise RuntimeError('ccp send sms network error')
        rs_data = rs.read()
        rs_data = json.loads(rs_data)
        if rs_data.get('statusCode') != '000000':
            raise RuntimeError('ccp send sms network error: %s' % rs_data.get('statusMsg'))

        return verify_code

