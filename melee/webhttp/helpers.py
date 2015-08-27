# -*- coding: utf-8 -*-

import random
import hmac, hashlib, time
from melee.core import json

def format_ok_response(data=None):
    from flask import jsonify
    return jsonify(meta={'code': 200, 'message': 'ok'}, data=data) if data is not None else jsonify(meta={'code': 200, 'message': 'ok'})

def format_str_response(src, code=200):
    from flask import make_response
    return make_response((src, code, None))

def generate_verifycode_image(value=None, size=(200, 100), length=4):
    '''
    生成图片验证码的response
    '''
    chars='345689abcdefghjkmnpqrstuvwxy'

    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    width, height = size
    img = Image.new('RGB', size, color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    def draw_points():
        '''绘制干扰点'''
        for w in xrange(width):
            for h in xrange(height):
                tmp = random.randint(0, 100)
                if tmp > 80:
                    draw.point((w,h), fill=(random.randint(1,255), random.randint(1,255), random.randint(1,255)))
        for x in xrange(30):
            draw.line((random.randint(1, width), random.randint(1, height), random.randint(1, width), random.randint(1, height)), fill=(random.randint(1,255), random.randint(1,255), random.randint(1,255)))
    def draw_value(value):
        '''生成指定长度的验证码'''
        font = ImageFont.truetype(font='./Monaco.ttf', size=50)
        font_width, font_height = font.getsize(value)
        delta_width = width-font_width
        delta_height = height-font_height
        draw.text((random.randint(0, delta_width/2), random.randint(0, delta_height/2)), value, font=font, fill=(250, 0, 0))
    
    value = value or ''.join(random.sample(chars, length))
    draw_value(value)
    draw_points()

    # 图形扭曲参数 
    params = [
        1-float(random.randint(1, 2))/100,
        0,0,0,
        1-float(random.randint(1, 10)/100),
        float(random.randint(1, 2)/500),
        0.001,
        float(random.randint(1, 2)/500)
    ]
    img = img.transform(size, Image.PERSPECTIVE, params)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    return img, value


def generate_verifycode_response(**kwargs):
    '''参数同generate_verifycode_image， 生成一个验证码response'''
    img, value = generate_verifycode_image(**kwargs)
    import StringIO
    buf = StringIO.StringIO()
    img.save(buf, 'JPEG', quality=70)
    response = format_str_response(buf.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response, value


def send_test_request(client, url, content, sig_kv=None, sig_key=None, files=None, post=True, getparams=None):
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
        if getparams:
            data.update(getparams)
        query_string = '&'.join(['%s=%s' % (k,v) for k,v in data.iteritems()])
        rs =  client.get(url, query_string=query_string)
    return rs.status_code, rs.data

def send_test_str_request(client, url, data):
    rs = client.post(url, data=data)
    return rs.status_code, rs.data

def get_valid_phone(phone):
    if not phone:
        return phone
    if len(phone) == 14:
        phone = phone[3:]
    if not phone.startswith('1'):
        phone = None
    if phone and not len(phone) == 11:
        phone = None
    return phone


