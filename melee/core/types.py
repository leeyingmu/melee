# -*- coding: utf-8 -*-

class DictEnum(dict):
    def __getattr__(self, name):
        if name in self:
            return self.get(name)
        raise AttributeError
    def clear(self): raise NotImplementedError
    def update(self): raise NotImplementedError
    def pop(self): raise NotImplementedError
    def popitem(self): raise NotImplementedError

class SetEnum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
    def add(self): raise NotImplementedError
    def clear(self): raise NotImplementedError
    def update(self): raise NotImplementedError