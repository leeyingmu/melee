# -*- coding: utf-8 -*-

import time, datetime, uuid

def format_time(dt, pattern=None):
    ''':param dt: instance of datetime.datetime'''
    pattern = pattern or '%Y-%m-%d %H:%M:%S'
    return time.strftime(pattern, dt.timetuple())

def past_seconds(dt):
    ''':param dt: instance of datetime.datetime'''
    return (datetime.datetime.now()-dt).seconds

def uuid1():
    return uuid.uuid1().hex

