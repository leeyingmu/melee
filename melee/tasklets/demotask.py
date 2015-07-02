# -*- coding: utf-8 -*-

from melee.core.env import meleeenv

logger = meleeenv.logging.getLogger('template.tasklet.demo')

if __name__ == '__main__':
    import time, sys
    sleepseconds = 3
    if len(sys.argv) == 2:
        sleepseconds = int(sys.argv[1])
    while True:
        logger.info('demotask say hello %s' % time.time())
        time.sleep(sleepseconds)