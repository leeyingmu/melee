# -*- coding: utf-8 -*-

import sys, os
from melee.core.env import meleeenv
from melee.webhttp import *

config = meleeenv.config
logger = meleeenv.logger

app = MeleeApp(__name__)

if __name__ == '__main__':
    app.run()
