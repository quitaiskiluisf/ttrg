#! /usr/bin/env python3

import argparse

class CmdConfig(object):
    ''' Manages the configuration parameters supplied via commandline arguments. '''

    @classmethod
    def get(cls):
        ''' Gets a dictionary containing the parameters set by commandline arguments.'''
        dsc = 'TTRG - Totvs TBC Report Generation Tool'

        p = argparse.ArgumentParser(description=dsc)
        p.add_argument('-c', '--codcoligada', required=True, help='TODO', type=int, )
        p.add_argument('-r', '--idreport', required=True, help='TODO', type=int, )
        p.add_argument('-f', '--filters', required=True, help='TODO', )
        p.add_argument('-p', '--params', required=True, help='TODO', )
        p.add_argument('-o', '--output', required=True, help='TODO', )

        p.add_argument('-v', '--version', action='version', version='%(prog)s DEV', )

        return vars(p.parse_args())
