#!/usr/bin/env python 

'''
probe yes

Just for testing purposes.
Always return 0 (OK).
'''

from oasispackage.interfaces import BaseProbe
import sys


class yes(BaseProbe):
    """
    Fake probe, just for testing purpopses.
    Always return 0
    """

    def __init__(self, options):
        super(yes, self).__init__(options)

    def run(self):
        return 0


if __name__ == '__main__':
    probe = yes(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)


