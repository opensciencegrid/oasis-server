#!/usr/bin/env python   

#
#  FIXME : temporary name
#

#
#  FIXME : 
#  getting oasis config object and projects config object 
#  is done more than once, in different __init__() methods
#

import commands
import datetime
import getopt
import logging
import logging.handlers
import os
import pwd
import re
import subprocess
import string
import sys
import time
import threading
import traceback

from ConfigParser import SafeConfigParser

from oasispackage.projects import Project, ProjectBasicConfig, ProjectFactory, ProjectThreadMgr
from oasispackage.flagfiles import FlagFile, FlagFileManager, FlagFileParser

major, minor, release, st, num = sys.version_info


# =============================================================================
#
#           A P I    C L A S S E S 
#
# =============================================================================


class oasisCLI(object):
    '''
    This class contains the methods to be used
    when the ID invoking them is a regular non-root user,
    for example when calling from the condor wrapper

    Methods that regular users are authorized to run are
    those related with pre-install steps and to run the payload.
    Methods to pass probes and publish are in a different class,
    invoked only by root. 
    '''

    def __init__(self, conffile=None):

        # 
        #  !!! FIXME !!!
        #  
        # this class has some code in common with class oasisd()
        # maybe they both should inherit from a base class
        #

        self.conffile = conffile  # path to oasis.conf

        self.block = False
        #   block == True means process does retain prompt and waits in a loop
        #   block == False means abort and message asking user to try again later 
        # This variable, if so, is set directly by client bin/oasis-user-publish, just by doing
        #       self.oasis.block = block
        # therefore, if we change the name from block to something better,
        # the client bin/oasis-user-publish needs to be fixed too.

        self.probes_rc = 0  # ?? do we need it ??

        try:
            self.oasisconf = self._getbasicconfig()
            self.username = self._getusername()
            self.projectsection = self._getprojectsection()
            # FIXME
            # there is no yet a self.log. 
            # use __logerror() within _getbasicconfig(), _getusername() and _getprojectsection()
        except:
            self.__logerror()
            sys.exit(1)

        self._setuplogging()

        # get the Project object for that project
        try:
            self.project = Project(self.projectsection, self.oasisconf)
            # FIXME: use ProjectFactory()
        except Exception, ex:
            self.log.critical('object Project can not be created. Error message = "%s". Aborting' %ex)
            self.console.critical('Internal OASIS malfunction. Error message = "%s". Aborting' %ex)
            raise ex

        self.log.debug('Object oasisCLI created.')


    # --------------------------------------------------------------
    #      P R E L I M I N A R I E S
    # --------------------------------------------------------------

    def __logerror(self):
        '''
        this method is just to log somehow that
        the configuration could not be read, 
        '''

        #
        # Maybe it should log to some system standard location
        # like  /var/log/messages  or similar        
        # for the time being we log into /var/log/oasis/oasis.log
        # which we assume is world wide writeable 
        #
        
        error = logging.getLogger()

        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'

        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream = logging.FileHandler('/var/log/oasis/oasis.log')
        logStream.setFormatter(logfile_formatter)
        error.addHandler(logStream)
        error.setLevel(logging.DEBUG)
        
        error.critical('Configuration cannot be read. Aborting.')


    def _setuplogging(self):
        '''
        creates two loggers:
            -- self.log to print in a log file all relevant messages
            -- self.console to send to stdout only those messages relevant to the users
        '''

        # FIXME  those names 'logfile' and 'user' are part of the message FORMAT. Use something less ugly
        self.log = logging.getLogger('logfile')
        self.console = logging.getLogger('user')

        # set the messages format
        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] <${user}:${project}> %(name)s %(filename)s:%(lineno)d : %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] <${user}:${project}> %(name)s : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] <${user}:${project}> %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] <${user}:${project}> %(name)s : %(message)s'

        LOGFILE_FORMAT = string.Template(LOGFILE_FORMAT)
        LOGFILE_FORMAT = LOGFILE_FORMAT.substitute(user=self.username, project=self.projectsection)
        STDOUT_FORMAT = string.Template(STDOUT_FORMAT)
        STDOUT_FORMAT = STDOUT_FORMAT.substitute(user=self.username, project=self.projectsection)

        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        stdout_formatter = logging.Formatter(STDOUT_FORMAT)

        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
        stdout_formatter.converter = time.gmtime  # to convert timestamps to UTC
       
        logStream = logging.FileHandler('/var/log/oasis/oasis.%s.log' % self.projectsection)

        logStream.setFormatter(logfile_formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(logging.DEBUG)  
       
        logStdout = logging.StreamHandler(sys.stdout)
        logStdout.setFormatter(stdout_formatter)
        self.console.addHandler(logStdout)
        # FIXME 
        # the log level is hardcoded
        # It should be either a config variable
        # or a input variable like  --oasisloglevel=DEBUG
        self.console.setLevel(logging.DEBUG)  


    # --------------------------------------------------------------

    def _getbasicconfig(self):
        '''
        returns a ConfigParser object for oasis.conf
        the variable self.conffile is setup by the client /usr/bin/oasis
        '''

        oasisconf = SafeConfigParser()
        #oasisconf.readfp(open("/etc/oasis/oasis.conf"))
        oasisconf.readfp(open(self.conffile))

        return oasisconf


    def _getusername(self):
        '''
        get the username of whoever is calling this API
        '''
        
        #username = getpass.getuser()
        username = pwd.getpwuid(os.getuid()).pw_name  

        return username


    def _getprojectsection(self):
        '''
        finds out the section in oasisprojects.conf corresponds 
        with the UNIX ID, a.k.a. self.username, running this process.
        '''
        # FIXME !! this is also done in Project() class


        # first get the OASIS projects ConfigFile
        oasisprojectsconffilename = self.oasisconf.get('PROJECTS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))

        # second get the section name  
        project = self.__getprojectsectionfromuser(oasisprojectsconf, self.username)
        if project:
            return project
        else:
            raise Exception

    def __getprojectsectionfromuser(self, conf, username):
        '''
        the private method just search for which section in a config object
        contains the spcified username, and returns the project variable.
        oasisprojects.conf looks like this

                [PROJ1]
                foo = bar
                user = blah
                project = PROJ1

                [PROJ2]
                foo2 = barz
                user = bloh
                project = proj2

        We need to find out the <section> given the user.
        Only reason the section name is not the username itself is just aesthetic,
        so we need to do this reverse lookup, at least for the time being.
        '''

        for section in conf.sections():
            if conf.get(section, 'user') == username:
                if conf.getboolean(section, 'enabled'):
                    return section
        return None


    # ======================================================

    def run(self, args):
        '''
        main method, called directly from the client /usr/bin/oasis

        args is a python list with the user payload and input options.
        For example, the result of sys.argv[]

        Steps done by this method:

            1. calls the preinstall() step

            2. runs the user payload

            3. calls the postinstall() step, which basically prepares the flagfile

            4. waits in a loop for the daemon to finish its part
               and marks the flagfile as <done>

            5. if no timeout, delete the flagfile a exit
        '''

        #
        # !!  FIXME !!
        # check if passing args as a python list (result of sys.argv[]) is the best way to do it.
        #

        inittime = time.time()

        cycle = 0
        nextmessagein = 0

        #while True:
        #
        #    listflagfiles = self._searchflagfiles()
        #    if listflagfiles == []:
        #        # no flagfile, jump out of the loop
        #        break
        #    else:
        #        # the presence of a flagfile may be relevant or not, 
        #        # depending on the underlying technology for file distribution.
        #        lock = self.project.distributionplugin.shouldlock( listflagfiles )
        #        # FIXME we are checking if we should lock or not on every cycle
        #        #       maybe it is better to search for flagfiles and check if lock
        #        #       before the loop. 
        #        #       However, I am not sure if that is risky 
        #        #       (like a new flagfile appears before next cycle and we miss it
        #        #       because we did not check it again)
        #
        #        if lock:
        #            # there is a flagfile, wait a little bit
        #            elapsed = time.time() - inittime
        #            if elapsed < self.project.starttimeout:
        #                if elapsed >= nextmessagein: 
        #                    waitingtime = 60*(2**cycle)
        #                    cycle += 1
        #                    nextmessagein = elapsed + waitingtime
        #                    self.log.warning('There is already a flagfile, meaning a previous installation job is still running. Waiting %s minutes' %(waitingtime/60))
        #                    self.console.warning('There is already a flagfile, meaning a previous installation job is still running. Waiting %s minutes' %(waitingtime/60))
        #            else:
        #                self.log.critical('Timeout reached and previous flagfile still there. Aborting.')
        #                self.console.critical('Timeout reached and previous flagfile still there. Aborting.')
        #                return 1
        #
        #    time.sleep(10)  # FIXME why 10?? should be a config variable?


        rc = self.preinstall()
        if rc != 0:
            self.log.critical('preinstall step failed. Aborting.')
            self.console.critical('preinstall step failed. Aborting.')
            return rc

        rc = self.runpayload(args)
        if rc != 0:
            self.log.critical('installation step failed. Aborting.')
            self.console.critical('installation step failed. Aborting.')
            return rc

        rc = self.publish()
        if rc != 0:
            self.log.critical('installation step failed. Aborting.')
            self.console.critical('installation step failed. Aborting.')

        self.log.debug('Leaving with rc=%s' %rc)
        return rc



    ###def _checknoflagfile(self):
    ###    '''
    ###    checks if there is already a flagfile for this project
    ###    '''
    ###
    ###    flagfile = FlagFile(self.project.projectname)
    ###
    ###    # in the future, we may return different RC, depending on the status,
    ###    # and react differently
    ###    # For example, a flagfile in "done" or "failed" should disappear quite soon
    ###    # so it would make sense to wait. 
    ###    if flagfile.search('request'):
    ###        return 1
    ###    if flagfile.search('probes'):
    ###        return 1
    ###    if flagfile.search('done'):
    ###        return 1
    ###    if flagfile.search('failed'):
    ###        return 1
    ###
    ###    # no flagfile
    ###    return 0


    def publish(self):
        '''
        runs both, postinstall() and _loop() methods
        '''

        self.log.info('Starting publishing.')
        self.console.info('Starting publishing.')

        rc = self.postinstall()
        if rc != 0:
            self.log.critical('postintall step failed. Aborting.')
            self.console.critical('postintall step failed. Aborting.')
            return rc

        rc = self._loop()
        self.log.info('Publishing finished with rc=%s' %rc)
        self.console.info('Publishing finished with rc=%s' %rc)
        return rc




    def _wait(self):

        inittime = time.time()

        cycle = 0
        nextmessagein = 0

        while True:

            listflagfiles = self._searchflagfiles()
            if listflagfiles == []:
                # no flagfile, jump out of the loop
                break
            else:
                if self.block == False:
                # block == False means abort and message asking user to try again later 
                    self.log.critical('There is currently a publishing process going on. Aborting.')
                    self.console.critical('There is currently a publishing process going on. Aborting. Try it again in a while.')
                    return 1
                else:
                    # block == True means process does retain prompt and waits in a loop

                    # the presence of a flagfile may be relevant or not, 
                    # depending on the underlying technology for file distribution.
                    lock = self.project.distributionplugin.shouldlock( listflagfiles )
                    # FIXME we are checking if we should lock or not on every cycle
                    #       maybe it is better to search for flagfiles and check if lock
                    #       before the loop. 
                    #       However, I am not sure if that is risky 
                    #       (like a new flagfile appears before next cycle and we miss it
                    #       because we did not check it again)

                    if lock:
                        # there is a flagfile, wait a little bit
                        elapsed = time.time() - inittime
                        if elapsed < self.project.starttimeout:
                            if elapsed >= nextmessagein: 
                                waitingtime = 60*(2**cycle)
                                cycle += 1
                                nextmessagein = elapsed + waitingtime
                                self.log.warning('There is already a flagfile, meaning a previous installation job is still running. Waiting %s minute(s)' %(waitingtime/60))
                                self.console.warning('There is already a flagfile, meaning a previous installation job is still running. Waiting %s minute(s)' %(waitingtime/60))
                        else:
                            self.log.critical('Timeout reached and previous flagfile still there. Aborting.')
                            self.console.critical('Timeout reached and previous flagfile still there. Aborting.')
                            return 1

            time.sleep(30)  # FIXME why 30?? should be a config variable?

        return 0







    def _searchflagfiles(self):
        '''
        searches for all flagfiles 
        '''
        mgnr = FlagFileManager() 
        listflagfiles = mgnr.search()
        return listflagfiles


    def _loop(self):
        '''
        loop waiting for flagfile to be changed by the daemon
        '''
        # FIXME ?? is a while loop the best way to implement it???

        self.log.debug('Start')

        projectname = self.project.projectname

        inittime = time.time()
        while True:

            # FIXME
            # check if this class already has a flagfile object
            # that can be reused
            #
            flagfile = FlagFile(projectname)
               
            flagfilepath = flagfile.search('done')
            if flagfilepath:
                self.log.debug('content of flagfile \n%s' %flagfile.read())

                #self.console.debug('output from the OASIS daemon \n%s' %flagfile.read())
                self.console.debug('output from the OASIS daemon:')
                out = self._parse_flagfile(flagfile)
                for line in out:
                    self.console.debug(line)

                flagfile.clean()
                return 0

            flagfilepath = flagfile.search('failed')
            if flagfilepath:
                self.log.error('content of flagfile \n%s' %flagfile.read())

                #self.console.error('output from the OASIS daemon \n%s' %flagfile.read())
                self.console.error('output from the OASIS daemon:')
                out = self._parse_flagfile(flagfile)
                for line in out:
                    self.console.error(line)
                    

                flagfile.clean()
                return 1

            # checking for timeout
            time.sleep(30)  # FIXME  why 30 ?? Should it be a config variable ??
            elapsed = time.time() - inittime
            if elapsed > self.project.finishtimeout:
                self.log.critical('timeout while waiting for the daemon to transfer and publish new content. Aborting.')
                self.console.critical('timeout while waiting for the daemon to transfer and publish new content. Aborting.')
                flagfile.search('request')
                flagfile.clean() 
                return 1

        # loop is done 
        self.log.debug('Leaving')
        return 0


    def _parse_flagfile(self, flagfile):
        '''
        the FlagFileParser::_parseoutput() methods
        digests the XML from the flagfile and returns things like this:

            [{u'elapsedtime': '0', u'inittime': '2014-06-26 14:19:53.635266', u'probe': 'yes', u'endtime': '2014-06-26 14:19:53.671395', u'rc': '0'},
             {u'elapsedtime': '0', u'inittime': '2014-06-26 14:19:53.674400', u'probe': 'yes', u'endtime': '2014-06-26 14:19:53.706200', u'rc': '0'}, 
             {u'inittime': '2014-06-26 14:19:53.708806', u'probe': 'filesize', u'elapsedtime': '0', u'rc': '0', u'endtime': '2014-06-26 14:19:53.743948', u'out': 'Probe passed OK. Output of cmd "find /home/oasis/mis -size +1G -type f -exec ls -lh {} \\;" was\n \n'}
            ]

            [{u'elapsedtime': '0', u'inittime': '2014-06-25 17:01:41.808788', u'out': 'Repository whitelist is expired!', u'endtime': '2014-06-25 17:01:41.864304', u'rc': '256'}]

            [{u'elapsedtime': '0', u'inittime': '2014-06-25 17:01:41.866973', u'out': 'Repository whitelist is expired!', u'endtime': '2014-06-25 17:01:41.916937', u'rc': '256'}]
        '''

        parser = FlagFileParser()

        content = flagfile.read()
      
        out = [] 

        # parsing XML related probes
        dicts = parser._parseoutput(content, 'probe')
        for i in dicts:
            line = 'probe %s started at %s and run for %s seconds with RC=%s' %(i['probe'], i['inittime'], i['elapsedtime'], i['rc'])
            out.append(line)

        # parsing the XML related transfer files
        dicts = parser._parseoutput(content, 'transfer')
        for i in dicts:
            line = 'file trasfers started at %s and run for %s seconds with RC=%s' %(i['inittime'], i['elapsedtime'], i['rc'])
            out.append(line)

        # parsing the XML related publishing 
        dicts = parser._parseoutput(content, 'publish')
        for i in dicts:
            line = 'publishing started at %s and run for %s seconds with RC=%s' %(i['inittime'], i['elapsedtime'], i['rc'])
            out.append(line)

        return out


    # -------------------------------------------------------------------------

    def preinstall(self):
        rc = self.project.preinstall()
        return rc

    def runpayload(self, args):
        rc = self.project.runpayload(args)
        return rc

    def postinstall(self):
        rc = self._wait()
        if rc != 0:
            return rc
        rc = self.project.postinstall()
        return rc



class oasisd(object):
    '''
    class to be invoked by the OASIS daemon.
    Includes steps that regular users are not authorized to perform:
        -- run probes
        -- transfer files
        -- publish
    '''

    def __init__(self):

        # 
        #  !!! FIXME !!!
        #  
        # this class has some code in common with class oasisCLI()
        # maybe they both should inherit from a base class
        #

        self.probes_rc = 0  # ?? do we need it ??

        # FIXME
        # maybe parsing the input options should have be done already
        # in that case, the client /usr/bin/oasisd
        # would call a factory class, instead of directly class oasisd() 
        self._parseopts()

        self._setuplogging()

        try:
            self.oasisconf = self._getbasicconfig()
            self.projectsconf = self._getprojectconfig()
        except:
            self.log.critical('Configuration cannot be read. Aborting.')
            sys.exit(1)

        self.log.debug('Object oasisd created.')


    # --------------------------------------------------------------
    #      P R E L I M I N A R I E S
    # --------------------------------------------------------------

    def _parseopts(self):
        '''
        parsing the input options.
        These inputs are setup in /etc/sysconfig/oasisd.sysconfig
        '''

        opts, args = getopt.getopt(sys.argv[1:], '', ['conf=', 'loglevel=', 'logfile='])
        for o, a in opts:

            # FIXME 
            # ?? should they have default values in case they are not passed from sysconfig ??
            if o == '--conf':
                self.conffile = a

            if o == '--loglevel':
                if a == 'debug':
                    self.loglevel = logging.DEBUG
                elif a == 'info':
                    self.loglevel = logging.INFO
                elif a == 'warning':
                    self.loglevel = logging.WARNING

            if o == '--logfile':
                self.logfile = a
        

    def _setuplogging(self):
        
        self.log = logging.getLogger()

        # set the messages format
        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
       
        logStream = logging.FileHandler(self.logfile)
        logStream.setFormatter(logfile_formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(self.loglevel)  
        

    # --------------------------------------------------------------

    def _getbasicconfig(self):
        '''
        returns a ConfigParser object for oasis.conf
        '''
        self.log.debug('Start')
        oasisconf = SafeConfigParser()
        oasisconf.readfp(open(self.conffile))
        self.log.debug('Leaving with config object %s' %oasisconf)
        return oasisconf

    def _getprojectconfig(self):
        '''
        returns a ConfigParser object for oasisproject.conf
        '''
        self.log.debug('Start')
        oasisprojectsconffilename = self.oasisconf.get('PROJECTS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))
        self.log.debug('Leaving with config object %s' %oasisprojectsconf)
        return oasisprojectsconf


    # ===========================================================================

    def runthreads(self):
        """
        creates an object ProjectThreadMgr and enters main loop
        This method is intended to be called by the daemon.
        """
        self.log.debug('Start')

        try: 
            self.log.info('creating ProjectThreadMgr object and entering main loop')
            self.projectthreadmgr = ProjectThreadMgr(self)
            self.projectthreadmgr.mainLoop()
        except KeyboardInterrupt:
            self.log.info('Caught keyboard interrupt - exitting')
            sys.exit(0)
        except ImportError, errorMsg:
            self.log.error('Failed to import necessary python module: %s' % errorMsg)
            sys.exit(0)
        except:
            self.log.error('Unexpected exception')
            self.log.error(traceback.format_exc(None))
            raise


