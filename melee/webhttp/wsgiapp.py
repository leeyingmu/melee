# -*- coding: utf-8 -*-

import sys, traceback, hmac, hashlib, time
from flask import Flask, Blueprint, request, g, json, jsonify, after_this_request
from ..core.env import config, logger, logging
from .exceptions import MeleeHTTPException, BadRequest, SignatureError, ServerError

class MeleeApp(object):

    def __init__(self, import_name):
        self.import_name = import_name
        self.app = Flask(import_name)

        self.logger = logging.getLogger('%s.api' % config.servicename)
        self.app.log = self.logger
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.teardown_request(self.teardown_request)
        self.app.register_error_handler(Exception, self.error_handler)

        for code in [400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414,
            415, 416, 417, 418, 422, 428, 429, 431, 500, 501, 502, 503, 504, 505]:
            self.app.register_error_handler(code, self.error_handler)

        logger.info('STARTUP', 'meleeapp %s started' % config.servicename)

    def verify_signature(self, sig_kv, signature, content):
        key = config.sigkey(str(sig_kv))
        if not key:
            return False
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        sig = hmac.new(key, content, hashlib.sha256).hexdigest()
        return sig == signature

    def before_request(self):
        self.logger.debug('REQUEST', request.url, request.endpoint, request.values.to_dict())
        g.rawdata = request.get_data(cache=True, parse_form_data=False)
        g.jsondata = {}
        if request.endpoint is None:
            return
        g.startms = int(time.time()*1000)

        content = request.values.get('content')
        signature = request.values.get('signature', '')
        sig_kv = request.values.get('sig_kv')

        if content:
            if not self.verify_signature(sig_kv, signature, content):
                raise SignatureError(description='Signature Not Correct.')
            try:
                g.jsondata = json.loads(content)
            except:
                g.jsondata = {}

        self.logger.debug('REQUEST', request.url, request.endpoint, g.jsondata)

    def teardown_request(self, exc):
        if exc:
            self.logger.error('SHOULD_NOT_HAPPEN','teardown_request, has exception:%s'%(exc))

    def after_request(self, response):
        if request.endpoint is None:
            return response
        if response is None:
            return response

        g.reqeust_cost = int(time.time()*1000) - g.startms

        if getattr(g, 'response_code', None) is None:
            code = response.status_code
        else:
            code = g.response_code  

        self.logger.info('REQUEST', request.remote_addr, request.method,
            request.url, request.headers.get('Content-Length', '0'), g.jsondata, 
            response.status_code, code, str(response.headers.get('Content-Length', '0')), json.loads(response.response[0]))

        return response

    def error_handler(self, error):
        self.logger.error('EXCEPTION', sys.exc_info()[1])
        self.logger.error('TRACEBACK', traceback.format_exc())
        
        if isinstance(error, MeleeHTTPException):
            g.response_code = error.code
            return jsonify(meta=error.info)
        else:
            error = ServerError(description='%s: %s' % (error.__class__.__name__, unicode(error)))
            g.response_code = error.code
            return jsonify(meta=error.info)


    def mount(self, blueprints, prefix=None):
        """bind the specific blueprints to the current flask app.
        :param blueprints: list, the list of blueprints
        :param prefix: dict, the url_prefix mapping definition for every blueprint
        Example Code:
            >>>blueprint = Blueprint('template', __name__, url_prefix='/test')
            >>>@blueprint.route('/foo')
            ...def foo():
            ...    return jsonify('foo ok')
            ...
            >>>meleeapp.mount([blueprint], prefix={'template': '/template'})
        now you can access the url 'http://host:port/template/test/xxx'
        """
        if not blueprints:
            return
        for b in blueprints:
            if prefix and b.name in prefix:
                url_prefix = '%s%s' % (prefix[b.name], b.url_prefix or '')
            else:
                url_prefix = b.url_prefix
            self.app.register_blueprint(b, url_prefix=url_prefix)
            self.logger.info('STARTUP', 'register blueprint: %s' % url_prefix)


    def __call__(self, environ, start_response):
        """Mark this MeleeApp as a WSGI App
        So all middleware that support WSGI protoal can run the instance of it.
        """
        return self.app(environ, start_response)



    # def run_server(self):
    #     from docopt import docopt
    #     arguments = docopt(runserver_usage, help=True)

    #     from werkzeug.serving import run_simple
    #     options = {}
    #     options.setdefault('use_reloader', True)
    #     options.setdefault('use_debugger', True)
        
    #     run_simple(arguments['--host'], int(arguments['--port']), self, **options)

    # def run_initdb(self):
    #     from docopt import docopt
    #     arguments = docopt(initdb_usage, help=True)

    #     from ..redynadb import redyna_manager
    #     redyna_manager.init_models()
    #     return 0


    # def run_command(self):
    #     from commandr import Run
    #     sys.argv.pop(1)
    #     return Run()


    # def run_task(self):
    #     from ..common.tasklet import run_tasklet
    #     sys.argv.pop(1)
    #     task_conf = {}
    #     for name, value in config.items():
    #         if 'tasklet' in value:
    #             for name, param in value['tasklet'].items():
    #                 param.update(name=name)
    #                 task_conf[name] = param
    #     run_tasklet('runtask', task_conf)

    # def run(self):
    #     """
    #     Prepares manager to receive command line input. Usually run
    #     inside "if __name__ == "__main__" block in a Python script.
    #     """

    #     if len(sys.argv) == 1:
    #         print(usage)
    #         sys.exit(0)

    #     command = sys.argv[1].lower()
    #     funcs = {
    #         'runserver': self.run_server,
    #         'initdb': self.run_initdb,
    #         'runcommand': self.run_command,
    #         'runtask': self.run_task,
    #     }
    #     func = funcs.get(command)

    #     if not func:
    #         if command not in ['-h', '--help']:
    #             print('Command %s is not supported\n'%(command))
    #         print(usage)
    #         sys.exit(-1)
    #     sys.exit(func())

        
