# -*- coding: utf-8 -*-

'''第三方支付回调接口'''

import sys, traceback, flask, datetime
from flask import Flask, Blueprint, request, g, json, jsonify
from ..core import json
from ..webhttp import helpers, BadRequest
from .callbackpay import BeeCloudPay, logger

blueprint = Blueprint('callbackpay', __name__, url_prefix='/callbackpay')

@blueprint.before_request
def before_request():
    g.url = request.url
    g.query_string = request.query_string
    headers = {}
    for k, v in request.headers or {}:
      headers[k.lower()] = v
    g.headers = headers
    g.jsondata = json.loads(g.rawdata)
    g.jsondata.update(request.values.to_dict())


@blueprint.route('/beecloud/<appid>/<melee_secret>', methods=['GET', 'POST'])
def beecloud_pay_callback(appid, melee_secret):
    g.appid = appid
    g.melee_secret = melee_secret
    g.jsondata.update({
        'appid': appid,
        'melee_secret': melee_secret
        })
    try:
        pay = BeeCloudPay.verify_request(g)
        pay.process()
        return helpers.format_str_response('success')
    except BadRequest as e:
        logger.error('payreceipt', 'beecloud', 'badrequest', appid, g.jsondata, e.description)
        logger.error('EXCEPTION', sys.exc_info()[1])
        logger.error('TRACEBACK', traceback.format_exc())
        return helpers.format_str_response('bad request: %s' % e.description)
    except:
        logger.error('payreceipt', 'beecloud', 'failed', appid, g.jsondata)
        logger.error('EXCEPTION', sys.exc_info()[1])
        logger.error('TRACEBACK', traceback.format_exc())
        return helpers.format_str_response('server failed')
