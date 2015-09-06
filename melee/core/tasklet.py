# -*- coding: utf-8 -*-
"""
Common backgroup process execution framework.
You can define a .py file and run it by using the ``tasklet`` framework which will
handle the process's life cycle automatically。

Example Code:

"""
import os, sys, pkgutil, time, signal
from subprocess import Popen
from .env import config, logger, logging

class Tasklet(object):
    """
    One tasklet is one subprocess which runs the specific module
    """

    def __init__(self, name, module, args):
        """
        :param name: the tasklet's name in the config
        """
        self.logger = logging.getLogger('%s.tasklet.%s' % (config.servicename, name))

        self.name = name
        self.package, self.module_name = module.rsplit('.', 1)
        self.filename = '%s.py' % self.module_name

        package_loader = pkgutil.find_loader(self.package)
        self.filepath = package_loader.filename

        self.cmds = [sys.executable, os.path.join(self.filepath, self.filename)]
        if args:
            self.cmds.extend(args.split())
        self.process = None
        self.startms = None

    def __str__(self):
        return 'tasklet %s %s %s' % (self.process.pid if self.process else '     ', self.name, self.cmds) 

    def start(self):
        self.process = Popen(self.cmds, cwd=os.getcwd())
        self.startms = int(time.time()*1000)
        self.logger.info('%s started' % self.name)

    def terminate(self):
        if self.process:
            self.process.terminate()
        self.logger.warn('termimated', str(self))

    def kill(self):
        if self.process:
            self.process.kill()
        self.logger.warn('killed', str(self))


class TaskletManager(object):
    """
    The main process used to run all tasklets by using a ``Tasklet``
    """

    def __init__(self, tasklets):
        self.logger = logging.getLogger('%s.taskletmanager' % config.servicename)

        self.tasklets = tasklets
        
        # register system signals
        for s in ['SIGINT', 'SIGTERM', 'SIGQUIT']:
            signal.signal(getattr(signal, s), getattr(self, 'handle_%s' % s))

    def handle_SIGINT(self, sig, frame):
        self.stopall()
        self.logger.info('stop all for SIGINT')

    def handle_SIGTERM(self, sig, frame):
        self.stopall()
        self.logger.info('stop all for SIGTERM')

    def handle_SIGQUIT(self, sig, frame):
        self.stopall()
        self.logger.info('stop all for SIGQUIT')

    def stopall(self):
        if self.tasklets:
            for t in self.tasklets:
                t.kill()
        sys.exit()

    def startall(self):
        if not self.tasklets:
            self.logger.info('there are not any tasklets defined, exit')
            sys.exit()

        for t in self.tasklets:
            t.start()
        self.logger.info('all tasklets started')

        while True:
            # wait for signals
            signal.pause()

    @classmethod
    def get(cls, tasklets_configs=None):
        """
        :param tasklets_configs: the tasklets configures
                                 [
                                    {'name': '', 'module': 'melee.tasklet.demotask', 'args': '1 2 3', 'number': 2}
                                 ]
        """
        if not tasklets_configs:
            return None
        tasklets = []
        for c in tasklets_configs:
            number = int(c.get('number') or 1)
            for i in xrange(number):
                tasklets.append(Tasklet(c.get('name'), c.get('module'), c.get('args')))
        return TaskletManager(tasklets)
