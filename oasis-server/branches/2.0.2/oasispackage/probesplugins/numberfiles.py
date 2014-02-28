#!/usr/bin/env python 

from oasispackage.interfaces import BaseProbe


class numberfiles(BaseProbe):
    """
    TO BE IMPLEMENTED

    checks the number of files in scratch area.
    Maybe some min and max limits
    Maybe insert .cvmfscatalogsdir if needed
    """

    def run(self):
        return 0
