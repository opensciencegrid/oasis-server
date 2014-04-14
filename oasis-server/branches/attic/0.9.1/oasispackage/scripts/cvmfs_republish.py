#!/usr/bin/env python 

"""
script (maybe temporary) 
that creates a file (quick&dirty solution for the time being)
and enter in a loop
waiting for the oasis daemon to see it and run the cvmfs publish script.
Once that file is gone, or a timeout happens,
the loop ends
"""

import datetime
import os
import sys
import time

from ConfigParser import SafeConfigParser


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
        
        self.path = pluginsconf.get('PublishcvmfsFile', 'path')
        self.timelimit = pluginsconf.getint('PublishcvmfsFile', 'timeout')

        self.rc = None

    def create_file(self):
        '''
        creates a file for the oasis daemon
        '''
    
        if os.path.exists(self.path):
            self.rc = 1
        else:
            os.system('touch %s' %self.path)
            self.rc = 0
    
    def main_loop(self):
        '''
        wait until the file is gone (becase oasis deleted it)
        or until a time limit is reached. 
        '''
    
        inittime = datetime.datetime.now()
        
        while True:
            if not os.path.exists(self.path):
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
    pub.create_file()
    if pub.rc:
        # file already exists !!
        return pub.rc
    pub.main_loop()
    return pub.rc

rc = main()
sys.exit(rc)

