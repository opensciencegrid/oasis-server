#!/usr/bin/env python 

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
        ##self.log.debug('calling probe <yes> for vo %s' %self.oasis.vo)
        return 0


if __name__ == '__main__':
    probe = yes(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)


