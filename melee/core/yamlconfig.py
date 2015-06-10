# -*- coding: utf-8 -*-

import yaml

class YamlConfig(dict):

    def __init__(self, config_file=None):
        if not config_file:
            return
        with open(config_file) as f:
            self.update(yaml.load(f) or {})

    def __getattr__(self, key):
        return self.get(key, None)

    
