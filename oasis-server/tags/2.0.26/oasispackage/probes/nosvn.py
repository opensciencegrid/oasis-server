#!/usr/bin/env python 

'''
probe nosvn 

Delete hidden directories .svn
'''

#
#  !! TO BE IMPLEMENTED !!
#


from oasispackage.interfaces import BaseProbe
import sys


class nosvn(BaseProbe):

    def __init__(self, options):
        super(nosvn, self).__init__(options)

    def run(self):
        return 0

if __name__ == '__main__':
    probe = nosvn(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

