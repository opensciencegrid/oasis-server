#!/usr/bin/env python 

from oasispackage.interfaces import BaseProbe


class forbiddenfiles(BaseProbe):
    """
    TO BE IMPLEMENTED

    checks that not file is forbidden, for security reasons.
    """

    def run(self):
        return 0
