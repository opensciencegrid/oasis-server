#!/usr/bin/env python 

'''
probe filesize

checks no file is larger than 1 GB.
'''

from oasispackage.interfaces import BaseProbe

import commands
import getopt
import sys

class filesize(BaseProbe):

    def __init__(self, options):
        super(filesize, self).__init__(options)

    def run(self):
       
        cmd = 'find %s -size +1G -type f' %self.rootdir
        out = commands.getoutput(cmd)
        if out == '':
            return 0
        else:
            # FIXME for the time being, it is just a print 
            print 'filesize probe failed. Output of cmd %s was %s' %(cmd, out)
            return 1


if __name__ == '__main__':
    probe = filesize(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

