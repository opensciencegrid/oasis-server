#!/usr/bin/env python 

'''
probe numberfiles

checks the number of files in scratch area.
'''

#
#  !! TO BE IMPLEMENTED !!
#

from oasispackage.interfaces import BaseProbe
import sys

class numberfiles(BaseProbe):

    def __init__(self, options):
        super(numberfiles, self).__init__(options)

    def run(self):
	
	# ?? Maybe some min and max limits ??
	# ?? Maybe insert .cvmfscatalogsdir if needed ??

        return 0


if __name__ == '__main__':
    probe = number(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

