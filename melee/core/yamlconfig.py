# -*- coding: utf-8 -*-

import yaml

class YamlConfig(dict):

    def __init__(self, config_file=None):
        if not config_file:
            return
        with open(config_file) as f:
            self.update(yaml.load(f) or {})

    @property
    def servicename(self):
        return self.get('main', {}).get('servicename') or 'template'

    @property
    def log(self):
        log = self.get('main', {}).get('log') or {}
        log['rootname'] = self.servicename
        return log

    def sigkey(self, sig_kv):
        return self.get('main', {}).get('request', {}).get('sigkeys', {}).get(sig_kv)

    @property
    def tasklets(self):
        return self.get('tasklets')




    
