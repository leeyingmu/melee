# -*- coding: utf-8 -*-

"""
All exceptions definitions used in apps based melee framework.
Example:
    >>>error = BadReqeust(description='username must be provided', extra={'error_type': 'param_error'})
    >>>error.info
    {'code': 400, 'message': 'BadReqeust', 'description': 'username must be provided', 'error_type': 'param_error'}
If the client want to know the detail error information, you can define them in the extra.

"""

from werkzeug.exceptions import HTTPException

class MeleeHTTPException(HTTPException):
    code = None
    description = None

    def __init__(self, description=None, extra=None):
        '''
        :param extra: the extra message returned to the client, must be ``dict``
        '''
        self.description = description or self.description
        self.extra = extra
        if self.extra and not isinstance(self.extra, dict):
            raise AttributeError('extra must be dict')
        if self.extra:
            for k in ['code', 'message', 'description']:
                if k in self.extra:
                    raise AttributeError('extra can not have the following key: code, message, description')

    @property
    def info(self):
        rs = {
            'code': self.code,
            'message': self.__class__.__name__,
        }
        if self.description:
            rs['description'] = self.description
        if self.extra and isinstance(self.extra, dict):
            rs.update(self.extra)
        return rs

    @property
    def response(self):
        '''must be using in the application context
        return one ``flask.Response`` isinstance, with the ``self.info`` json string in the response body
        '''
        from flask import jsonify
        return jsonify(self.info)



class BadRequest(MeleeHTTPException):
    code = 400

class SignatureError(BadRequest):
    pass

class ServerError(MeleeHTTPException):
    code = 500

class NeedRetry(MeleeHTTPException):
    code = 500


