# -*- coding: utf-8 -*-

import os, sys, traceback, hmac, hashlib, time
import flask
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

        @self.app.route('/')
        def helloworld():
            # return flask.make_response(('wellcome to melee!', 200, None))
            return 'wellcome to melee!'

        self._init()

        logger.info('STARTUP', 'meleeapp %s created' % config.servicename)

    def _init(self):
        # init the rds sql connections
        self.rdsdb = None
        if config.rds_binds:
            app_config = {'SQLALCHEMY_BINDS': config.rds_binds}
            for k, v in config.rds_pool_config.iteritems():
                app_config['SQLALCHEMY_%s' % k.upper()] = v
            self.app.config.update(app_config)
            from flask.ext.sqlalchemy import SQLAlchemy
            self.rdsdb = SQLAlchemy(self.app)
            logger.info('init SQLALCHEMY rds', config.rds_binds.keys(), app_config)

    def verify_signature(self, sig_kv, signature, content, timestamp):
        key = config.sigkey(str(sig_kv))
        if not key:
            return False
        rawdata = '%s%s'% (content, timestamp)
        if isinstance(content, unicode):
            rawdata = rawdata.encode('utf-8')
        sig = hmac.new(key, rawdata, hashlib.sha256).hexdigest().lower()
        return sig == signature.lower()

    def before_request(self):
        self.logger.info('REQUEST', '%s?%s' % (request.path, request.query_string), request.endpoint, request.data or request.values.to_dict(), request.headers.get('User-Agent'))
        g.rawdata = request.data
        g.jsondata = {}
        if request.endpoint is None:
            return
        g.startms = int(time.time()*1000)

        content = request.values.get('content')
        signature = request.values.get('signature', '')
        sig_kv = request.values.get('sig_kv')
        timestamp = request.values.get('timestamp') or 0
        g.jsonpcallback = request.values.get('callback')

        if content:
            if not timestamp or (time.time()*1000)-int(timestamp) > 86400000:
                raise BadRequest(description='request expired %s' % timestamp)

            if not self.verify_signature(sig_kv, signature, content, timestamp):
                raise SignatureError(description='Signature Not Correct.')
            try:
                g.jsondata = json.loads(content)
            except:
                g.jsondata = {}


    def teardown_request(self, exc):
        if exc:
            self.logger.error('SHOULD_NOT_HAPPEN','teardown_request, has exception:%s'%(exc))

    def after_request(self, response):
        if request.endpoint is None:
            return response
        if response is None:
            return response

        g.request_cost = int(time.time()*1000) - g.startms

        if getattr(g, 'response_code', None) is None:
            code = response.status_code
        else:
            code = g.response_code

        # 支持jsonp, 解决ajax get 请求跨域问题
        #if g.jsonpcallback:
            #response.response = '%s(%s)' % (g.jsonpcallback, response.response)
        response.headers['Access-Control-Allow-Origin'] = '*'

        self.logger.info('REQUEST', request.remote_addr, request.method, g.request_cost,
            '%s?%s' % (request.path, request.query_string), request.headers.get('Content-Length', '0'), g.jsondata, 
            response.status_code, code, response.response, str(response.headers.get('Content-Length', '0')))

        return response

    def error_handler(self, error):
        self.logger.error('EXCEPTION', sys.exc_info()[1])
        self.logger.error('TRACEBACK', traceback.format_exc())
        
        if isinstance(error, MeleeHTTPException):
            g.response_code = error.code
            return jsonify(meta=error.info)
        else:
            error = ServerError(description=getattr(error, 'message', error.__class__.__name__))
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
            self.logger.info('STARTUP', 'register blueprint %s: %s' % (b.name, url_prefix))


    def __call__(self, environ, start_response):
        """Mark this MeleeApp as a WSGI App
        So all middleware that support WSGI protoal can run the instance of it.
        """
        return self.app(environ, start_response)


    def runserver(self, arguments):
        # @self.app.route('/')
        # def helloworld():
        #     # return flask.make_response(('wellcome to melee!', 200, None))
        #     return 'wellcome to melee!'

        from werkzeug.serving import run_simple
        options = {}
        options.setdefault('use_reloader', True)
        options.setdefault('use_debugger', True)
        logger.info('STARTUP', 'meleeapp %s started' % config.servicename)
        run_simple(arguments['--host'], int(arguments['--port']), self, **options)


    def runtasklet(self, arguments):
        self.logger.debug(config.servicename, 'tasklets starting ...')
        from ..core.tasklet import TaskletManager
        tasklet_manager = TaskletManager.get(config.tasklets)
        tasklet_manager.startall()


    def initdb(self, arguments):
        self.logger.info(config.servicename, 'start intidb ...')
        self.rdsdb.create_all()
        if config.baiduyun_ak:
            from ..baiduyun.lbs import LBSTable
            for c in LBSTable.__subclasses__():
                self.logger.info('init baiduyun table', c.__tablename__, c.init_schema(config.baiduyun_ak))
        self.logger.info(config.servicename, 'end intidb')

    def run(self):
        usage = """MeleeApp Running in Command-Line

        runserver: run the wsgiserver in one process
        runtasklet: run all tasklets defined in the config file in one parent process with subprocesses

        Usage:
          server.py runserver [--host=<host>] [--port=<port>]
          server.py runtasklet [--pythonpath=<pythonpath>] [--chdir=<chdir>]
          server.py initdb [--baiduyun]

        Options:
          -h --help                         Show this
          --host=<host>                     the host used to run the server [default: 127.0.0.1]
          --port=<port>                     the port used to run the server [default: 5000]
          --pythonpath=<pythonpath>         Add additonal python sys.path.
          --chdir=<chdir>                   Chdir to specified directory before apps loading.  

        """

        from docopt import docopt
        arguments = docopt(usage)
        # process common command options
        self._process_cmd_options(arguments)

        if arguments['runserver']:
            return self.runserver(arguments)
        elif arguments['runtasklet']:
            return self.runtasklet(arguments)
        elif arguments['initdb']:
            return self.initdb(arguments)
        else:
            print(usage)
            raise RuntimeError('not supported command')

    def _process_cmd_options(self, arguments):
        if arguments['--pythonpath']:
            paths = arguments['--pythonpath'].split(',')
            for path in reversed(paths):
                if os.path.exists(path) and os.path.isabs(path):
                    sys.path.insert(0, path)
        if arguments['--chdir']:
            os.chdir(arguments['--chdir'])


app = MeleeApp(__name__)

        
