#!/usr/bin/env python 

'''
probe no

Just for testing purposes.
Always returns 1 (failed).
'''

from oasispackage.interfaces import BaseProbe
import sys


class no(BaseProbe):
    """
    Fake probe, just for testing purpopses.
    Always return 1
    """

    def __init__(self, options):
        super(no, self).__init__(options)

    def run(self):
        return 1


if __name__ == '__main__':
    probe = no(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)

