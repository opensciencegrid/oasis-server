#!/usr/bin/env python 

# -----------------------------------------------
#   
#   Base class for all probe plugins
#
# -----------------------------------------------

import logging
import os


class BaseProbe(object):
    def __init__(self, vo, conf, section):
        """
        'vo' is the VO
        'conf' is a ConfigParser object with probes specs for that VO
        'section' is the section is that config object for a given probe plugin
        """

        self.vo = vo
        self.conf = conf
        self.section = section
    
        self.scratch = os.environ['OASIS_USER_WORKING_DIRECTORY']

        self.log = logging.getLogger('main.probes')

    def run(self):
       raise NotImplementedError
