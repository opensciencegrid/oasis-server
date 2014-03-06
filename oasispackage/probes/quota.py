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

        opts, args = getopt.getopt(self.options, '', ['limit='])
        for o, a in opts:
            if o == '--limit':
                self.limit = int(a)

    def run(self):

        cmd = 'du -s %s | awk \'{print $1}\'' %self.rootdir
        out = commands.getoutput(cmd)
        out = int(out)

        if out > self.limit:
            return 1
        else:
            return 0


if __name__ == '__main__':
    probe = qouta(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)
