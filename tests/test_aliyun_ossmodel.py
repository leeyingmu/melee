# -*- coding: utf-8 -*-

import unittest, random, json
from melee.core.env import config
from melee.aliyun.ossmodel import OSS2ImgObject

class DemoImg(OSS2ImgObject):
    __base_path__ = 'test'
    __bucket_name__ = config.imageoss.get('bucket_name')
    __endpoint__ = config.imageoss.get('endpoint')
    __access_key_id__ = config.imageoss.get('access_key_id')
    __access_key_secret__ = config.imageoss.get('access_key_secret')
    __urldomain__ = 'img.dev.hclz.me'
    __action_separator__ = '@'
    __style_separator__ = '@!'

class TestBase(unittest.TestCase):

    def test(self):
        f = open('tests/testimageoss.png', 'rb')
        path = 'testcase'
        img = DemoImg.upload(f, path=path, filename=f.name.split('/')[-1])
        url = img.url(style='teststyle')
        print url
        img2 = DemoImg.url_parse(url)
        self.assertEqual(img.filename, img2.filename)
        self.assertEqual(img.path, img2.path)







