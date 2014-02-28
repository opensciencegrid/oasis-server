#!/usr/bin/env python 

'''
probe quota

checks if the project went overquota
'''

#
#  !! TO BE IMPLEMENTED !!
#

from oasispackage.interfaces import BaseProbe
import sys

class quota(BaseProbe):

    def __init__(self, options):
        super(quota, self).__init__(options)

    def run(self):
        return 0


if __name__ == '__main__':
    probe = qouta(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)
