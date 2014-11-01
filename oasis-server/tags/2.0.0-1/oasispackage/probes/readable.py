#!/usr/bin/env python 

'''
probe readable

makes sure all files are readable with the world? the UNIX group oasis?
'''

#
#  !! TO BE IMPLEMENTED !!
#

from oasispackage.interfaces import BaseProbe
import sys

class readable(BaseProbe):

    def __init__(self, options):
        super(readable, self).__init__(options)

    def run(self):
	
        return 0


if __name__ == '__main__':
    probe = readable(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

