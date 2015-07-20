# -*- coding: utf-8 -*-

import unittest, hmac, hashlib
from flask import Blueprint, jsonify
from melee.core import json
from melee.core.env import meleeenv
config = meleeenv.config
logger = meleeenv.logger

from melee.webhttp import MeleeApp, helpers
from melee.webhttp.exceptions import *

meleeapp = MeleeApp(__name__)

blueprint = Blueprint('template', __name__, url_prefix='/test')

@blueprint.route('/ok', methods=['GET', 'POST'])
def foo():
    return helpers.format_ok_response(data={})

@blueprint.route('/badrequest', methods=['GET', 'POST'])
def badrequest():
    raise BadRequest()

@blueprint.route('/servererror', methods=['GET', 'POST'])
def servererror():
    raise RuntimeError('test error')

meleeapp.mount([blueprint], prefix={'template': '/template'})


class Test(unittest.TestCase):
    sig_kv = '1'
    sig_key = config.sigkey(sig_kv)

    @classmethod
    def setUpClass(cls):
        meleeapp.app.config["TESTING"] = True
        meleeapp.app.config["DEBUG"] = True
        cls.app = meleeapp.app.test_client()


    @classmethod
    def tearDownClass(cls):
        pass

    def send_request(self, url, content):
        rs = None
        try:
            _, rs = helpers.send_test_request(self.app, url, content, sig_kv=self.sig_kv, sig_key=self.sig_key)
        finally:
            print '------> %s, %s, %s' % (url, json.dumps(content), rs)
        return json.loads(rs)

    def test_ok(self):
        url = '/template/test/ok'
        content = {
            'test': 'ok'
        }
        rs = self.send_request(url, content)
        self.assertEqual(200, rs.get('meta').get('code'))
        self.assertEqual('ok', rs.get('meta').get('message'))

        self.assertEqual({}, rs.get('data'))


    def test_badrequest(self):
        url = '/template/test/badrequest'
        content = {}
        rs = self.send_request(url, content)
        self.assertEqual(400, rs.get('meta').get('code'))
        self.assertEqual('BadRequest', rs.get('meta').get('message'))


    def test_signature_error(self):
        self.sig_key = 'f'*32
        url = '/template/test/ok'
        content = {}
        rs = self.send_request(url, content)
        self.assertEqual(400, rs.get('meta').get('code'))
        self.assertEqual('SignatureError', rs.get('meta').get('message'))
        self.sig_key = config.sigkey(self.sig_kv)


    def test_servererror(self):
        url = '/template/test/servererror'
        content = {}
        rs = self.send_request(url, content)
        self.assertEqual(500, rs.get('meta').get('code'))
        self.assertEqual('ServerError', rs.get('meta').get('message'))



