# -*- coding: utf-8 -*-

import logging
import logging.handlers
import lln

class MeleeLogger(logging.getLoggerClass()):

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        if isinstance(msg, str) and msg.lower() in ['traceback', 'exception']:
            l = ['EXCEPTION ']
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
        name = name or self.rootname
        if name not in self.loggers:
            self.loggers[name] = self.createLogger(name)
        return self.loggers.get(name)

    def createLogger(self, name):
        """create a logger using all the handlers
        """
        logger = logging.getLogger(name)
        level = str(self.levels.get(name, None) or self.levels.get('default')).upper()
        logger.setLevel(level)
        for handler_name in self.handlers:
            h = None
            if handler_name == 'null':
                h = logging.NullHandler()
            elif handler_name == 'stdout':
                h = logging.StreamHandler()
            elif handler_name == 'file':
                h = logging.handlers.TimedRotatingFileHandler(self.filename, when='D', interval=1)
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
        logger.debug('test debug')
        logger.info('test info')
        logger.warn('test warn')
        logger.error('test error')
        logger.critical('test critical')
        try:
            def raiseerror():
                raise RuntimeError('test error')
            raiseerror()
        except:
            # logger.error('EXCEPTION', exc_info=sys.exc_info())
            logger.error('TRACEBACK', traceback.format_exc())
    meleelogging = MeleeLogging(rootname='melee', filename='/tmp/template.log', handlers=['stdout', 'file'], levels={'melee.example': 'debug'})
    logger = meleelogging.getLogger('melee.example')
    test(logger)






