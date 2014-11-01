#!/usr/bin/env python   

'''
Exception classes for OASIS
'''

class ConfigurationFailure(Exception):
    """
    config file can not be read
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

