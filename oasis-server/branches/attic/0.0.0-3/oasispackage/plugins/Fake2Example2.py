#!/usr/bin/env python 


import logging

__author__ = "Jose Caballero"
__copyright__ = "2012 Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov"
__status__ = "Development"


class Fake2Example2(object):

    def __init__(self, task):
        '''
        task is an object of Task Class.
        It is a reference to the object that runs this plugin.

        This plugin does not do anything. 
        Just add an entry to the log file.
        '''

        self.log = logging.getLogger("main.fake2example2")

        self.log.info('fake2example2: Object initialized.')

    def run(self):
        '''
        actual set of actions to be done by this plugin 
        '''

        self.log.debug('run: Starting.')
        self.log.info('run: Fake2Example2 plugin alive')
        self.log.debug('run: Leaving.')
   
