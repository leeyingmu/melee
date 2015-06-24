# -*- coding: utf-8 -*-
'''
basic core tools used by other modules in melee
'''
import sys, os, pkgutil
from .outers import *
from .log import MeleeLogging

class MeleeEnv(object):
    '''the melee runtime environment'''

    def __init__(self, config_file='config.yaml'):
        if os.path.isabs(config_file):
            self.config_file = config_file
        else:
            self.config_file = os.path.join(os.getcwd(), config_file)

        # init the configuration
        self.init_config()
        self.init_logger()
        self.init_statsd()


    def init_config(self):
        from .yamlconfig import YamlConfig
        self.config = YamlConfig(config_file=self.config_file)

    def init_logger(self):
        self.logging = MeleeLogging(**self.config.log)
        self.logger = self.logging.getLogger(self.config.servicename)
        self.logger.info('logger init success')

    def init_statsd(self):
        pass

    # def _get_root_path(import_name):
    #     """Returns the path to a package or cwd if that cannot be found.  This
    #     returns the path of a package or the folder that contains a module.
    #     """
    #     if not import_name:
    #         return os.getcwd()
    #     # Module already imported and has a file attribute.  Use that first.
    #     mod = sys.modules.get(import_name)
    #     if mod is not None and hasattr(mod, '__file__'):
    #         return os.path.dirname(os.path.abspath(mod.__file__))

    #     # Next attempt: check the loader.
    #     loader = pkgutil.get_loader(import_name)

    #     # Loader does not exist or we're referring to an unloaded main module
    #     # or a main module without path (interactive sessions), go with the
    #     # current working directory.
    #     if loader is None or import_name == '__main__':
    #         return os.getcwd()

    #     filepath = loader.get_filename(import_name)

    #     return os.path.dirname(os.path.abspath(filepath))


meleeenv = MeleeEnv()
config = meleeenv.config
logger = meleeenv.logger





