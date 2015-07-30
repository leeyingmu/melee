# -*- coding: utf-8 -*-

import hmac, hashlib, time
from melee.core import json

def format_ok_response(data=None):
    from flask import jsonify
    return jsonify(meta={'code': 200, 'message': 'ok'}, data=data) if data is not None else jsonify(meta={'code': 200, 'message': 'ok'})

def send_test_request(client, url, content, sig_kv=None, sig_key=None, files=None, post=True):
    t = int(time.time()*1000)
    content = json.dumps(content)
    rawdata = '%s%s' % (content, t)
    sig = hmac.new(sig_key, rawdata, hashlib.sha256).hexdigest()
    data = {
        'content': content,
        'timestamp': t,
        'signature': sig,
        'sig_kv': sig_kv
    }
    if post:
        if files:
            data.update(files)
        rs = client.post(url, data=data)
    else:
        query_string = '&'.join(['%s=%s' % (k,v) for k,v in data.iteritems()])
        rs =  client.get(url, query_string=query_string)
    return rs.status_code, rs.data


