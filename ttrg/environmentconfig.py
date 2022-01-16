#! /usr/bin/env python3

import configparser
import sys

class EnvironmentConfig(object):
    ''' Manages configuration parameters related to the environment, reading them from the .ini file. '''

    @classmethod
    def get_mandatory(cls, key):
        ''' Gets a setting from the .ini file. Raises KeyError if the key is not found. '''
        cfg = configparser.ConfigParser()
        cfg.read(sys.argv[0] + '.ini')

        if 'ttrg' not in cfg:
            raise Exception('The config file does not contain a section named "ttrg".')

        return cfg['ttrg'][key]


    @classmethod
    def get(cls, key, default=None):
        ''' Gets a setting from the .ini file. Returns None or default if the key was not found. '''
        try:
            v = cls.get_mandatory(key)
        except KeyError:
            v = default

        return v
