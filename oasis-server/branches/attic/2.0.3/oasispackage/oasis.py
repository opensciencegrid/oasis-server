#!/usr/bin/env python 

import commands
import getpass
import logging
import os
import sys
import time

from ConfigParser import SafeConfigParser
from string import Template

major, minor, release, st, num = sys.version_info



class oasisCLI(object):

    def __init__(self):

        self.probes_rc = 0

        self._setuplogging()

        try:
            self._getconfigs()
        except:
            self.log.critical('Configuration cannot be read. Aborting.')
            sys.exit(1)

        self._changelogformat()


    # --------------------------------------------------------------
    #      P R E L I M I N A R I E S
    # --------------------------------------------------------------

    def _getconfigs(self):
        '''
        read all config files and setup all relevant attributes
        '''

        # get the generic OASIS configuration 
        self.oasisconf = SafeConfigParser()
        self.oasisconf.readfp( open("/etc/oasis/oasis.conf"))

        # get the OASIS users configuration
        self.usersconf = SafeConfigParser()
        self.usersconf.readfp( open("/etc/oasis/oasisusers.conf"))

        # find out the VO 
        self.username = getpass.getuser()
        self.vo = self.usersconf.get(self.username, "VO")
        # try to get VO from x509, and interpolate just in case
        #try:    
        #    st, vo = commands.getstatusoutput('voms-proxy-info -vo')
        #    if st == 0:
        #        vo_temp = Template(self.vo)
        #        self.vo = vo_temp.substitute(VO_FROM_X509, vo) 
        #except:
        #    pass

        # find out OSG_APP
        self.osg_app = self.usersconf.get(self.username, "OSG_APP")
        # if needed, interpolate
        osg_app_env = os.environ.get("OSG_APP", None)
        if osg_app_env:
            osg_app_temp = Template(self.osg_app)
            self.osg_app = osg_app_temp.substitute(OSG_APP_FROM_ENV, osg_app_env)
            

        # get the OASIS probes configurations
        self.oasisprobesconf = self.oasisconf.get('PROBES', 'oasisconf')
        self.oasisvoconfdir = self.oasisconf.get('PROBES', 'vodirectoryconf')
        self.oasisvoprobesconf = '%s/%s.conf' %(self.oasisvoconfdir, self.vo)


    def _setuplogging(self):

        
        self.log = logging.getLogger()

        # set the messages format
        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s : %(message)s'
        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        stdout_formatter = logging.Formatter(STDOUT_FORMAT)
        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
        stdout_formatter.converter = time.gmtime  # to convert timestamps to UTC
        
        ### adding a handler for a /var/log/ file
        logStream = logging.FileHandler('/var/log/oasis/oasis.log')
        logStream.setFormatter(logfile_formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(logging.DEBUG)  # default
        
        ### adding a handler for stdout (to be read by the users)
        logStdout = logging.StreamHandler(sys.stdout)
        logStdout.setFormatter(stdout_formatter)
        logStdout.setLevel(logging.INFO) # a more restrictive level for this handler
        self.log.addHandler(logStdout)
        

    def _changelogformat(self):
        """
        adding the username and VO to the logfile messages
        """

        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] <${user}:${vo}> %(name)s %(filename)s:%(lineno)d : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] <${user}:${vo}> %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'


        LOGFILE_FORMAT = Template(LOGFILE_FORMAT)
        LOGFILE_FORMAT = LOGFILE_FORMAT.substitute(user=self.username, vo=self.vo)
        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
        
        for h in self.log.handlers:
            if isinstance(h, logging.FileHandler):
                h.setFormatter(logfile_formatter)
        

# ===========================================================================
#                   A C T I O N S 
# ===========================================================================

    def preinstall(self):
        """
        things to be done before running the user payload
        """
        self._syncronize_back()


    def _syncronize_back(self)
        """
        ensure the user scratch area has a perfect copy of what 
        is currently in the repo
        """
        pass


    def runpayload(self, payload):
        '''
        payload is the result of sys.argv[1:]
        For example:
           ['/var/lib/condor/execute/dir_15018/condor_exec.exe', 'a', 'b', 'c', '1', '2', '3'] 
        '''
       
        self.payload = payload
        cmd = ' '.join(self.payload)

        self.log.info('Running installation job %s' %cmd)

        # temporary solution
        st, out = commands.getstatusoutput(cmd)

        if st == 0:
            self.log.info('Installation job finished OK')
        else:
            self.log.error('Installation job failed with RC=%s' %st)

        return st


    def postinstall(self):
        """
        things to be done just after running the user payload
        """
        self._prepareflag()

    def _prepareflag(self):
        """
        prepare flag to let the daemon to know publishing is requested
        Flag files can be, for example:

            /var/log/oasis/<vo>/job.XYZ.request
            /var/log/oasis/<vo>/job.XYZ.running            
            /var/log/oasis/<vo>/job.XYZ.done

        Comments:

            -- does that mean that the <vo> subdirectory already exists?
               If not, how creates it? Note that I am allowing multiple users per VO...

            -- the UNIX ID of the file owner 
               (the daemon needs to know that to drop privileges before running probes) 
               can be found with 

                    pwd.getpwuid( os.stat( <filename> ).st_uid ).pw_name

               or probes are run in a sub-shell with 'su'

            -- Maybe it does not make sense more than one user per VO. 
               One could not be able to modify what another one wrote... 
               (or rsync would fix that?)

        """
        flagfile = '/var/log/oasis/%s/job.request' %self.vo
        # create that flagfile, like 'touch'
        open(flagfile, 'w').close()
        


    def runprobes(self):
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

        #
        #   temporary implementation !!!
        #

        # 1st run the default OASIS probes
        if os.path.exists(self.oasisprobesconf):
            self.log.debug('running probes from config file %s' %self.oasisprobesconf)
            rc = self._runprobes(self.oasisprobesconf)
            if rc != 0:
                self.probes_rc = rc
                return rc

        # 2nd run the specific VO probes
        if os.path.exists(self.oasisvoprobesconf):
            self.log.debug('running probes from config file %s' %self.oasisvoprobesconf)
            rc = self._runprobes(self.oasisvoprobesconf)
            if rc != 0:
                self.probes_rc = rc
                return rc

        # if everything went OK... 
        self.log.info('all probes passed OK')
        return 0

    def _runprobes(self, conffile):

        try:
            probesconf = SafeConfigParser()
            probesconf.readfp(open(conffile))
        except:
            self.log.error('can not read probes configuration file')
            return 1
    
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
                probe_obj = probe_class(self, probesconf, conf_probe_name)
    
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
        self.log.debug('All probes from config file %s passed OK' %os.path.basename(conffile))
        return 0


    def publish(self):
        """
        first it calls to runprobes()
        If all probes run fine, then publish.

        Publishing is done by an specific plugin.
        """

        self._getdistributionplugin()
        rc = self.distribution_obj.publish() 
        if rc == 0:
            self.log.info('publishing done OK')
        else:
            self.log.critical('publishing failed')

        return rc


    def _getdistributionplugin(self):
        '''
        get the plugin for a given distribution tool, 
        i.e. cvmfs
        '''

        tool = self.oasisconf.get("DISTRIBUTION", "tool")
        distribution_plugin = __import__('oasispackage.distributionplugins.%s' %tool,
                                         globals(),
                                         locals(),
                                         ['%s' %tool])

        distribution_cls_name = tool
        distribution_cls = getattr(distribution_plugin, distribution_cls_name)
        self.distribution_obj = distribution_cls(self)
