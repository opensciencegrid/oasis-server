#!/usr/bin/env python 

"""
script (maybe temporary) 
that adds an entry to a DB (quick&dirty solution for the time being)
and enter in a loop
waiting for the oasis daemon to see it and run the cvmfs publish script.
Once that file is gone, or a timeout happens,
the entry is removed 
"""

import datetime
import os
import sys
import time

from ConfigParser import SafeConfigParser
from oasispackage.plugins.persistent import *


class publish(object):
    # -----------------------------------------------
    #           return codes 
    # -----------------------------------------------
    #   rc = 0  ->  everything went OK
    #   rc = 1  ->  file already exists
    #   rc = 2  ->  timeout and file still there
    # -----------------------------------------------
    
    
    # -------------------------------------------------------------
    # Value of path should be got from the plugins config file.
    # 
    # For the time being, we are going to hardcode the path 
    # to this config file.
    # It is supposed to be read from oasis config file. 
    #
    # The plugin we are interested is called PublishcvmfsFile
    # -------------------------------------------------------------

    def __init__(self):    

        oasisconf = SafeConfigParser()
        oasisconf.readfp( open('/etc/oasis/oasis.conf') )
        pluginsconfpath = oasisconf.get('OASIS', 'pluginsconf')
        
        pluginsconf = SafeConfigParser()
        pluginsconf.readfp( open(pluginsconfpath) )
        
        self.timelimit = pluginsconf.getint('PublishcvmfsDB', 'timeout')

        self.persistencedb = PersistenceDB(pluginsconf, Message)

        self.rc = None

    def create_message(self):
        '''
        writes an message in the db for the oasis daemon
        '''
    
        # ---------------------------------------------
        #   FIXME
        #    for the time being, we assume there can 
        #    be only one msg in the DB
        # ---------------------------------------------
        if len(self.persistencedb.messages) > 0:
            self.rc = 1
        else:
            # writes message
            self.persistencedb.session.add(Message(message='msg1'))
            self.persistencedb.save()
            self.rc = 0

    
    def main_loop(self):
        '''
        wait until the file is gone (becase oasis deleted it)
        or until a time limit is reached. 
        '''
    
        inittime = datetime.datetime.now()
        
        while True:
            # ---------------------------------------------
            #   FIXME
            #    for the time being, we assume there can 
            #    be only one msg in the DB
            # ---------------------------------------------
            # ---------------------------------------------
            #   FIXME
            #     what happened if the DB is gone (for some reason)?
            #     that should be reported with different rc
            # ---------------------------------------------
            self.persistencedb.refresh()
            if not len(self.persistencedb.messages) > 0:
                self.rc = 0
                break
            now = datetime.datetime.now() 
            delta = now - inittime
            if delta.seconds > self.timelimit:
                self.rc = 2
                break
            time.sleep(1)
    

def main():
    pub = publish()
    pub.create_message()
    if pub.rc:
        # file already exists !!
        return pub.rc
    pub.main_loop()
    return pub.rc

rc = main()
sys.exit(rc)

