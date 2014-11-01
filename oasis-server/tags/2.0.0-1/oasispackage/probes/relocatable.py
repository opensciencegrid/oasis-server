#!/usr/bin/env python 

'''
probe relocatable 

checks if some binary is linked to stuffs
in absolute paths that will not exist on the WN.
It could be directory specific, etc.
'''

#
#  !! TO BE IMPLEMENTED !!
#


from oasispackage.interfaces import BaseProbe
import sys


class relocatable(BaseProbe):

    def __init__(self, options):
        super(relocatable, self).__init__(options)

    def run(self):
        return 0

if __name__ == '__main__':
    probe = relocatable(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

