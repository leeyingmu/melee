# -*- coding: utf-8 -*-

import time, datetime, uuid

def format_time(dt, pattern=None):
    ''':param dt: instance of datetime.datetime'''
    if not dt:
        return None
    if isinstance(dt, (datetime.datetime, datetime.date)):
        timetuple = dt.timetuple()
    elif isinstance(dt, (int,str)):
        seconds = int(str(dt)[:10])
        timetuple = time.localtime(seconds)
    elif isinstance(dt, time.struct_time):
        timetuple = dt
    else:
        raise RuntimeError('not supported dt type')
    pattern = pattern or '%Y-%m-%d %H:%M:%S'
    return time.strftime(pattern, timetuple)

def past_seconds(dt):
    ''':param dt: instance of datetime.datetime'''
    return (datetime.datetime.now()-dt).seconds

def uuid1():
    return uuid.uuid1().hex

