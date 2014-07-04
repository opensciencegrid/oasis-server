#!/usr/bin/env python   

import logging
import logging.handlers
import sys
import time

major, minor, release, st, num = sys.version_info


class oasisLogger(object):
    """
    class just to create the base Loggers:
        -- logfile
        -- console
    """
    
    def __init__(self):

        self.log = logging.getLogger('logfile') 
        self.console = logging.getLogger('console')

        # set the messages format
        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ]  %(name)s %(filename)s:%(lineno)d : %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ]  %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ]  %(name)s : %(message)s'

        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        stdout_formatter = logging.Formatter(STDOUT_FORMAT)

        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
        stdout_formatter.converter = time.gmtime  # to convert timestamps to UTC
       
        logStream = logging.FileHandler('/var/log/oasis/oasis.log')  # Default log file
        logStream.setFormatter(logfile_formatter)
        self.log.addHandler(logStream)
       
        logStdout = logging.StreamHandler(sys.stdout)
        logStdout.setFormatter(stdout_formatter)
        self.console.addHandler(logStdout)

        self.log.setLevel(logging.DEBUG)  
        self.console.setLevel(logging.DEBUG)  


"""
Later on, logger attributes can be changed on real time.
For example:

    new_format = '%(asctime)s (UTC) - OASIS [ %(levelname)s ] <new ad-hoc stuff here>  %(name)s : %(message)s'
    new_formatter = logging.Formatter(new_format)
    log.handlers[0].setFormatter(new_formatter)

NOTE: Maybe not, since the new loggers do not have handlers, only the parent
"""
