# -*- coding: utf-8 -*-

import os, time
import logging
import logging.handlers
import lln


class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    '''自定义handler，修复原handler在日志切换rename报错导致日志丢失的bug'''

    def __init__(self, filename, **kwargs):
        self.filename = os.path.abspath(filename)
        self.dirname = os.path.dirname(self.filename)
        self._mkdirs()
        self.baseFilename = "%s.%s" % (self.filename, time.strftime("%Y-%m-%d"))
        logging.handlers.TimedRotatingFileHandler.__init__(self, self.baseFilename, **kwargs)

        print '++++++++++++++ __init__ +++++++++++'
        print 'self.rolloverAt =%s' % self.rolloverAt
        print 'self.rolloverAt =%s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.rolloverAt))

    def _mkdirs(self):  
        if not os.path.exists(self.dirname):  
            try:  
                os.makedirs(self.dirname)  
            except Exception,e:  
                print str(e)

    def doRollover(self): 
        print '++++++++++++++ doRollover +++++++++++'
        print 'self.rolloverAt =%s' % self.rolloverAt
        print 'self.rolloverAt =%s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.rolloverAt))
        self.stream.close()  
        # get the time that this sequence started at and make it a TimeTuple  
        self.baseFilename = "%s.%s" % (self.filename, time.strftime("%Y-%m-%d"))
        print self.baseFilename
        if self.encoding:  
            self.stream = codecs.open(self.baseFilename, 'a', self.encoding)  
        else:  
            self.stream = open(self.baseFilename, 'a')  
        self.rolloverAt = self.rolloverAt + self.interval
        print 'next self.rolloverAt =%s' % self.rolloverAt
        print 'next self.rolloverAt =%s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.rolloverAt))
        print '++++++++++++++ doRollover end +++++++++++'


class MeleeLogger(logging.getLoggerClass()):

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        if isinstance(msg, str) and msg.lower() in ['traceback', 'exception']:
            l = [msg.upper()]
            args = [arg if isinstance(arg, basestring) else repr(arg) for arg in args]
            l.extend(args)
            msg = '\n'.join(l).replace('\n', '\n####### ')
            args = None
        else:
            msgs = [msg]
            msgs.extend(args)
            msg = lln.dumps(msgs)
            args = None
        return super(MeleeLogger, self).makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra)

# overwrite the default LoggerClass
logging.setLoggerClass(MeleeLogger)


class MeleeLogging(object):

    """The uniform logger factory of the melee framework.
    You can configure the logger in the config.template.yaml in the home directory of your project.

    Configure example::
        handlers: ['stdout', 'file']
        levels:
            default: info
            example: debug
            example.rds: debug
        filname: /tmp/example.log

    Supporting handlers::
        stdout: the logging.StreamHandler
        file: the logging.handlers.TimedRotatingFileHandler

    Using example code::
        >>>meleelogging = MeleeLogging(rootname='melee', handlers=['stdout'], levels={'melee.example': 'debug'})
        >>>logger = meleelogging.getLogger('example')
        >>>logger2 = meleelogging.getLogger('example.m1')
        >>>logger.info('the root logger')
        >>>logger2.info('the sub logger')

    Custom handlers definition which will be added to all loggers in the meleelogging::
        >>>h = logging.StreamHandler()
        >>>h.setLevel(logging.INFO)
        >>>meleelogging.addHandler(h)

    """

    __formatter__ = logging.Formatter(
        '%(asctime)s.%(msecs)03d %(levelname)-8s|%(name)s|%(filename)s.%(funcName)s.%(lineno)s|%(message)s',
        '%Y-%m-%dT%H:%M:%S.%SS')

    def __init__(self, rootname='template', handlers=None, filename='/tmp/example.log', levels=None):
        self.rootname = rootname
        self.handlers = handlers or ['null']
        self.filename = filename
        self.levels = levels or {'default': 'info'}
        self.loggers = {}
        # handlers that users define by themselves.
        self._custom_handlers = []

    def getLogger(self, name):
        """get one logger which shares one instance in the same process.
        """
        name = '%s.%s' % (self.rootname, name) if name and name != self.rootname else self.rootname
        if name not in self.loggers:
            self.loggers[name] = self.createLogger(name)
        return self.loggers.get(name)

    def createLogger(self, name):
        """create a logger using all the handlers
        """
        logger = logging.getLogger(name)
        level = str(self.levels.get(name, None) or self.levels.get('default') or 'INFO').upper()
        logger.setLevel(level)
        # not propagate to father loggers
        logger.propagate = 0
        for handler_name in self.handlers:
            h = None
            if handler_name == 'null':
                h = logging.NullHandler()
            elif handler_name == 'stdout':
                h = logging.StreamHandler()
            elif handler_name == 'file':
                h = MyTimedRotatingFileHandler(self.filename, when='midnight', interval=1)
                # h = MyTimedRotatingFileHandler(self.filename, when='h', interval=1)
            if h:
                h.setLevel(level)
                h.setFormatter(self.__formatter__)
                logger.addHandler(h)
        for h in self._custom_handlers:
            logger.addHandler(h)
        return logger

    def addHandler(self, handler):
        """add one handler to all created loggers and the following creating loggers
        """
        if handler in self._custom_handlers:
            return False
        self._custom_handlers.append(handler)
        for name, logger in self.loggers.iteritems():
            logger.addHandler(handler)
        return True

if __name__ == '__main__':
    import sys, traceback
    def test(logger):
        # logger.debug('test debug')
        logger.info('test info')
        # logger.warn('test warn')
        # logger.error('test error')
        # logger.critical('test critical')
        # try:
        #     def raiseerror():
        #         raise RuntimeError('test error')
        #     raiseerror()
        # except:
        #     # logger.error('EXCEPTION', exc_info=sys.exc_info())
        #     logger.error('TRACEBACK', traceback.format_exc())
    meleelogging = MeleeLogging(rootname='melee', filename='/tmp/template.log', handlers=['stdout', 'file'], levels={'melee.example': 'debug'})
    logger = meleelogging.getLogger('melee.example')
    # logger2 = meleelogging.getLogger('melee.example2')
    # logger3 = meleelogging.getLogger('melee.example3')
    for i in xrange(10000):
        test(logger)
        # test(logger2)
        # test(logger3)
        time.sleep(10)






