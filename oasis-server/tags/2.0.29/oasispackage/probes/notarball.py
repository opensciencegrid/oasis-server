#!/usr/bin/env python 

'''
probe notarball

checks a tarball file is NOT included in the content.
'''

#
#  !! TO BE IMPLEMENTED !!
#

from oasispackage.interfaces import BaseProbe
import sys


class notarball(BaseProbe):

    def __init__(self, options):
        super(notarball, self).__init__(options)

    def run(self):
        return 0


if __name__ == '__main__':
    probe = notarball(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

