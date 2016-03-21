# -*- coding: utf-8 -*-

import urllib
import simplejson as json

class LLNFormatError(Exception):
    pass


def escape_string(data):
    if '\r' in data or '\n' in data or '\\' in data:
        return json.dumps(data, ensure_ascii=False)[1:-1]
    return unicode(data, 'utf-8') if isinstance(data, str) else data

def unescape_string(data):
    if '\\' in data:
        return json.loads('"%s"'%(data))
    return data


def dump_string(data):
    if not data:
        return '%s'%(data)
    data = escape_string(data)
    if '|' in data or '=' in data or data[0] == '$':
        return '$%d$ %s'%(len(data), data)
    else:
        return data

def dump_binop(left, right):
    left = '%s'%(left)
    right = '%s'%(right)
    right = escape_string(right)
    if '|' in left or '=' in left or '|' in right or left[0] == '$':
        return '$%d,%d$ %s=%s' % (len(left), len(right), left, right)
    else:
        return '%s=%s'%(left, right)

def dump_dict(data):
    try:
        d = json.dumps(data)
        if '|' in d  or d[0] == '$':
            return '$$%d$ %s' % (len(d), d)
        else:
            return '$%s' % (d)
    except:
        return dump_string(repr(data))

def dump_object(data):
    return dump_string(repr(data))

def dumps(msgs):
    s = []
    for msg in msgs:
        if msg is None:
            s.append('None')
        elif isinstance(msg, bool):
            s.append(str(msg))
        elif isinstance(msg, (int, float)):
            s.append(repr(msg))
        elif isinstance(msg, (str, unicode)):
            s.append(dump_string(msg))
        elif isinstance(msg, tuple):
            if len(msg) ==2:
                s.append(dump_binop(msg[0], msg[1]))
            else:
                s.append(dump_string(repr(msg)))
        elif isinstance(msg, (list, dict)):
            s.append(dump_dict(msg))
        else:
            s.append(dump_object(msg))
    return '|'.join(s)

def load_meta(s, i):
    m1 = s[i+1]
    if m1 == '{' or m1 == '[':
        return s[i]
    elif m1 == '$' or m1 in '0123456789':
        j = s.find('$ ', i+1)
        if j == -1:
            raise LLNFormatError('meta <%s> info not completed. <:> not found'%(s[i:]))
        else:
            return s[i:j+2]
    else:
        raise LLNFormatError('meta <%s> is invalid'%(s[i:]))


def load_data_withmeta(s, i, meta):
    meta = meta.rstrip()
    if meta == '$':
        string = load_string(s, i)
        return json.loads(string), len(string)
    exp = meta[1:-1].replace(' ', '')
    if not exp:
        raise LLNFormatError('meta <%s> is invalid'%(meta))
    if ',' in exp:
        pair = exp.split(',')
        if len(pair) != 2:
            raise LLNFormatError('meta <%s> only support one <,> now.'%(meta))
        llen, rlen = int(pair[0]), int(pair[1])
        left = s[i:i+llen]
        i += llen
        if s[i] != '=':
            raise LLNFormatError('LLN expect <=> but <%s> found.'%(s[i]))
        i += 1
        right = s[i:i+rlen]
        i += rlen
        return {left: unescape_string(right)}, llen+rlen+1
    elif exp[0] == '$':
        data_len = int(exp[1:])
        string = s[i:i+data_len]
        return json.loads(string), len(string)
    else:
        data_len = int(exp)
        string = s[i:i+data_len]
        return unescape_string(string), len(string)

def load_string(s, i):
    j = s.find('|', i)
    if j == -1:
        return s[i:]
    return s[i:j]


def loads(s):
    loaded = []
    check_separator = False
    i = 0
    while i < len(s):
        c = s[i]
        if check_separator:
            if c == '|':
                i += 1
                check_separator = False
                continue
            else:
                raise LLNFormatError('separator | expected, but <%s> found.'%(c))
        if c == '$':
            meta = load_meta(s, i)
            i += len(meta)
            data, length = load_data_withmeta(s, i, meta)
            loaded.append(data)
            i += length
        else:
            string = load_string(s, i)
            if '=' in string:
                loaded.append(dict((string.split('=', 1)[0:2], )))
            else:
                loaded.append(string)
            i += len(string)
        check_separator = True
    return loaded


if __name__ == '__main__':
    msgs = [
        'title',
        'test tuple',
        ('a', '1'),
        'test return\n\r\\test return',
        '$test json',
        {'a': 1, 'b':{'c':'3', 'd':[1,2,3,4], 'cn':'中文'}},
        'test 中文'
    ]
    l = dumps(msgs)
    m = loads(l)
