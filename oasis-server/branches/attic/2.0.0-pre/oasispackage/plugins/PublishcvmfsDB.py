#!/usr/bin/env python 


import commands
import logging

from persistent import *

__author__ = "Jose Caballero"
__copyright__ = "2012 Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov"
__status__ = "Development"



class PublishcvmfsDB(object):

    def __init__(self, task):
        '''
        task is an object of Task Class.
        It is a reference to the object that runs this plugin.

        This plugin searches for a message in a DB.
        If the message exists, then it run the CVMFS publishing script
        and removes the message.  
        '''

        self.log = logging.getLogger("main.publishcvmfsdb")

        self.pluginname = task.pluginname  # the name of the plugin (== name of the class)
        self.pluginsconf = task.pluginsconf

        self.log.info('publishcvmfsdb: Object initialized.')

    def run(self):
        '''
        actual set of actions to be done by this plugin 
        '''

        self.log.debug('run: Starting.')

        # I am not 100% sure, but I think I have to create the persistentdb
        # object everytime to prevent this error:
        #
        #   run: Caught exception: (ProgrammingError) SQLite objects created in a thread can only be used in that same thread
        #
        # unless I find another solution. 
        # Maybe I am not closing the session properly.
        self.persistencedb = PersistenceDB(self.pluginsconf, Message)

        if len(self.persistencedb.messages) > 0:
            # ------------------------------------------------------
            #   FIXME
            #     For the time being, we only search for a single
            #     message. We do not pay attention to its content
            # ------------------------------------------------------
            message = self.persistencedb.messages[0]
            text = message.message
            

            self.log.info('run: message %s exists. Running publish' %text)
            st, out = commands.getstatusoutput('/etc/cvmfs/cvmfs_publish.sh')
            self.log.info('run: CVMFS publish script finished with st=%s and out=%s' %(st, out))
            self.log.info('run: removing message %s from the DB' %text)
            self.persistencedb.session.delete(message)
            self.persistencedb.save()

        self.log.debug('run: Leaving.')
   
