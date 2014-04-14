#!/usr/bin/env python 

from base import BaseProbe


class no(BaseProbe):
    """
    Fake probe, just for testing purpopses.
    Always return 1
    """
    def run(self):
        self.log.debug('calling probe <no> for vo %s' %self.vo)
        return 1
