# -*- coding: utf-8 -*-
'''通用email发送工具'''


import smtplib
from email.mime.text import MIMEText
from email.header import Header

from .env import logging, config

logger = logging.getLogger('email')


class SMTPMail(object):
    ''''''

    def __init__(self, server, username, password, port=25):
        self.server = server
        self.username = username
        self.password = password
        self.port = port or 25


    def send(self, tolist, subject, content, html=True):
        '''
        :param tolist: `list` 接受邮件的地址列表
        :param content: `string` 邮件内容
        :param html: `bool` 是否发送html格式邮件
        '''
        msg = MIMEText(content, 'html' if html else 'plain', 'utf-8')
        msg['From'] = self.username
        msg['Subject'] = Header(subject, 'utf-8')

        smtp = smtplib.SMTP()
        smtp.connect(self.server, self.port)
        smtp.login(self.username, self.password)

        rs = smtp.sendmail(self.username, tolist, msg.as_string())
        logger.info('send to', tolist, subject, content, html, rs)
        smtp.quit()


    def send_simpletable(self, tolist, subject, tablename=None, headnames=None, datas=None):
        content = '<table style="width: 90%; ">'
        if tablename:
            content += '<caption>' + tablename + '</caption>'
        if headnames and isinstance(headnames, list):
            content += '<tr>'
            for name in headnames:
                content += '<th style="border: 1px #bbb solid; padding: 0; background-color: #ccc; font-weight: bold; height: 40px; line-height: 21px;">' + name + '</th>'
            content += '</tr>'
        if datas and isinstance(datas, list):
            for d in datas:
                if d and isinstance(d, list):
                    content += '<tr>'
                    for dv in d:
                        content += '<td style="border: 1px #bbb solid; padding: 0; height: 40px; line-height: 21px;">' + str(dv) + '</td>'
                    content += '</tr>'
        content += '</table>'
        return self.send(tolist, subject, content, html=True)


smtpclient = SMTPMail(config.email_config.get('server'), config.email_config.get('username'), config.email_config.get('password'))



