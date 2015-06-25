# -*- coding: utf-8 -*-

from melee.core.env import meleeenv

config = meleeenv.config
logger = meleeenv.logger

if __name__ == '__main__':
    logger.info('test log for service', config.servicename)
    logger.debug('test log for service', config.servicename)
    logger.warn('test log for service', config.servicename)
    logger.error('test log for service', config.servicename)
    logger.critical('test log for service', config.servicename)
