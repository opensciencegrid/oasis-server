#!/usr/bin/env python 

# -------------------------------------------------------------------
#
#     code to run all probes, as they are listed in a config file
#     and return a RC depending if all probes were passed or not
#
# -------------------------------------------------------------------

import logging
import os
import sys
import time
from ConfigParser import SafeConfigParser

class Probes(object):

    def __init__(self):

        self.vo = None
        self.conffile = None

        self.setuplog()

    def setuplog(self):
    
        major, minor, release, st, num = sys.version_info

        self.log = logging.getLogger()
        if major == 2 and minor == 4:
            #FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
            FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s : %(message)s'
        else:
            #FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
            FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s : %(message)s'
        formatter = logging.Formatter(FORMAT)
        formatter.converter = time.gmtime  # to convert timestamps to UTC

        ### adding a new handler, for a /var/log/ file
        logStream = logging.FileHandler('/var/log/oasis/oasis.log')
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(logging.DEBUG)  # default

        ### creating a handler, for stdout (to be read by the users)
        logStdout = logging.StreamHandler(sys.stdout)
        logStdout.setFormatter(formatter)
        logStdout.setLevel(logging.INFO) # a more restrictive level for this handler
        self.log.addHandler(logStdout)


        #self.log.setLevel(logging.DEBUG)
    
    def run(self):
        """
        probes config files, for each VO, looks like this 
        
              [probe1]
             
              enabled = True 
              probetype = nodelete
              directory = /blah/
              level = abort
        
              [probe2]
        
              enabled = True 
              probetype = test
              foo = bar
        """
    
        probesconf = SafeConfigParser()
        probesconf.readfp(open(self.conffile))
    
        # get list of probes
        list_probes = probesconf.sections()

        # get plugins for probes and run them 
        for conf_probe_name in list_probes:
            enabled = probesconf.getboolean(conf_probe_name, "enabled")
            if enabled:
                probe_type = probesconf.get(conf_probe_name, 'probetype')
                
                # get plugin for that probe
                probe_plugin = __import__('oasispackage.probesplugins.%s' %probe_type, 
                                          globals(),
                                          locals(),
                                          ['%s' %probe_type])
                probe_class_name = probe_type # name of class == name of plugin
                probe_class = getattr(probe_plugin, probe_class_name)        
   
                # get the object from the class
                probe_obj = probe_class(self.vo, probesconf, conf_probe_name)
    
                # run the plugin
                #self.log.info('calling probe <%s>' %probe_type)
                rc = probe_obj.run()
   
                if rc == 0:
                    self.log.info('probe <%s> passed OK' %probe_type)  # ?? should it be conf_probe_name ??
                else:
                    # if RC != 0, abort
                    self.log.critical('probe <%s> failed. Aborting.' %probe_type) # ?? should it be conf_probe_name ??
                    return rc
    
        # if all probes passed fine...
        self.log.info('All probes from config file %s passed OK' %os.path.basename(self.conffile))
        return 0
    


if __name__ == '__main__':
    probes = Probes()
    probes.vo = "atlas"
    probes.conffile = '/etc/oasis/probes.conf'
    rc = probes.run()
    sys.exit(rc)
