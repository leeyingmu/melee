# -*- coding: utf-8 -*-

import unittest, random, json, time
from melee.core.env import config
from melee.core.myemail import SMTPMail, smtpclient

class Test(unittest.TestCase):

    def test_text(self):
        m = SMTPMail('smtpdm.aliyun.com', 'serverop@mail.merben.cc', 'merben1234')
        m.send(['823647157@qq.com', 'yingmulee@163.com'], 'Test Text5', '来自melee测试邮件1', html=False)
        # m.send(['823647157@qq.com'], 'Test Html4', '<div style="color:red"><b>来自melee测试邮件2</b></div>')
    
    def test_table(self):
    	m = SMTPMail('smtpdm.aliyun.com', 'serverop@mail.merben.cc', 'merben1234')
    	m.send_simpletable(['823647157@qq.com', 'yingmulee@163.com'], 'Test Table1', tablename='Test Table Caption', headnames=['name', 'age'], datas=[['lee', 29], ['tom', 30]])

    def test_smtpclient(self):
    	smtpclient.send(['823647157@qq.com', 'yingmulee@163.com'], 'Test smtpclient ', '来自melee测试邮件1 %s' % time.time(), html=False)