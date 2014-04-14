#!/usr/bin/env python 

from oasispackage.interfaces import BaseProbe


class yes(BaseProbe):
    """
    Fake probe, just for testing purpopses.
    Always return 0
    """


    def run(self):
        self.log.debug('calling probe <yes> for vo %s' %self.oasis.vo)
        return 0
