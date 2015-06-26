# -*- coding: utf-8 -*-

import hmac, hashlib
from melee.core import json

def format_ok_response(data=None):
    from flask import jsonify
    return jsonify(meta={'code': 200, 'message': 'ok'}, data=data) if data is not None else jsonify(meta={'code': 200, 'message': 'ok'})

def send_test_request(client, url, content, sig_kv=None, sig_key=None, files=None, post=True):
    sig = hmac.new(sig_key, json.dumps(content), hashlib.sha256).hexdigest()
    data = {
        'content': json.dumps(content),
        'signature': sig,
        'sig_kv': sig_kv
    }
    if post:
        if files:
            content.update(files)
        rs = client.post(url, data=data)
    else:
        query_string = '&'.join(['%s=%s' % (k,v) for k,v in content.iteritems()])
        rs =  client.get(url, query_string=query_string)
    return rs.status_code, rs.data


