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

# -----------------------------------------------
#           return codes 
# -----------------------------------------------
#   rc = 0  ->  everything went OK
#   rc = 1  ->  file already exists
#   rc = 2  ->  timeout and file still there
# -----------------------------------------------


timelimit = 300 # 5 minutes
path = "/var/run/oasis/publish"

def create_file():
    '''
    creates a file for the oasis daemon
    '''
    if os.path.exists(path):
        return 1
    os.system('touch %s' %path)
    return 0

def main_loop():
    '''
    wait until the file is gone (becase oasis deleted it)
    or until a time limit is reached. 
    '''

    inittime = datetime.datetime.now()
    
    while True:
        if not os.path.exists(path):
            rc = 0
            break
        now = datetime.datetime.now() 
        delta = now - inittime
        if delta.seconds > timelimit:
            rc = 2
            break

    return rc 

def main():
    rc = create_file()
    if rc:
        # file already exists !!
        return rc
    rc = main_loop()
    return rc

rc = main()
sys.exit(rc)

