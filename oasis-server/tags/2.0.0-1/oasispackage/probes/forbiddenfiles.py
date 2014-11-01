#!/usr/bin/env python 

'''
probe forbiddenfiles 

checks that not file is forbidden, for security reasons.
'''

#
#  !! TO BE IMPLEMENTED !!
#


from oasispackage.interfaces import BaseProbe
import sys


class forbiddenfiles(BaseProbe):

    def __init__(self, options):
        super(forbiddenfiles, self).__init__(options)

    def run(self):
        return 0

if __name__ == '__main__':
    probe = forbiddenfiles(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

