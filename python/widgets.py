# Copyright (c) 2018 Xiaofan Li
# License: MIT

'''General widgets.'''

from __future__ import absolute_import, division, print_function, with_statement


class Enum(set):
    '''Simple enumeration.'''
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
