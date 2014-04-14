#!/usr/bin/env python 

from oasispackage.interfaces import BaseProbe


class relocatable(BaseProbe):
    """
    TO BE IMPLEMENTED

    this probe is supposed to check if some binary is linked to stuffs
    in absolute paths that will not exist on the WN.
    It could be directory specific, etc.
    """

    def run(self):
        return 0
