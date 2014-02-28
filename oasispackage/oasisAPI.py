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

major, minor, release, st, num = sys.version_info

class FlagFile(object):
    '''
    class to handle flag files.

    flagfiles are being used in OASIS for communcation between the two main
    processes -the user process and the daemon process-:

        -- the user process creates a flagfile after running the user payload
           to request publishing

        -- the daemon starts doing tasks (run probes, transfer files, publish...)
           when it sees that flagfile

        -- the daemon changes the name of the flagfile when done

        -- daemon may write some content in the flagfile during operations,
           the user process reads it.


    The format of the flagfile is like

        yyyy-mm-dd:hh-mm-ss.<project>.<status>
   
    where status can be:

            - request
            - probes
            - done
            - failed

    Example:   2014-01-23:15:20:36.MIS.request
    
    '''

    def __init__(self, projectname):
        '''
        '''
        # FIXME ?? should I pass a Project() object

        self.projectname = projectname
        # 
        # !! FIXME !!
        # Maybe read basedir from oasis.conf
        # which requires passing parent object as reference 
        # 
        self.basedir = '/var/log/oasis' 
        self.timestamp = None
        self.flagfile = None

    def create(self):
        '''
        creates the actual file in the filesystem.
        It is created with <status> "request" as last field of the filename

        The method also gives initial value to attribute self.flagfile
        with the whole path in the filesystem to the flagfile
        '''

        now = time.gmtime() # gmtime() is like localtime() but in UTC
        timestr = "%04d-%02d-%02d:%02d:%02d:%02d" % (now[0], now[1], now[2], now[3], now[4], now[5])

        self.flagfile = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, timestr,  'request'))
        open(self.flagfile, 'w').close() 

    def setprobes(self):
        '''
        modifies the <status> field to 'probes'.
        Updates the self.flagfile attribute
        '''

        new = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, self.timestamp, 'probes'))
        os.rename(self.flagfile, new) 
        self.flagfile = new

    def setdone(self):
        '''
        modifies the <status> field to 'done'.
        Updates the self.flagfile attribute
        '''

        new = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, self.timestamp, 'done'))
        os.rename(self.flagfile, new) 
        self.flagfile = new

    def setfailed(self):
        '''
        modifies the <status> field to 'failed'.
        Updates the self.flagfile attribute
        '''

        new = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, self.timestamp, 'failed'))
        os.rename(self.flagfile, new) 
        self.flagfile = new

    def search(self, status):
        '''
        searches in the filesystem for a flagfile with that particular <status>
        '''
        # !! FIXME !!
        # make it more generic, without requiring and input

        # !! FIXME !!
        # For the time being, it returns the first found file.
        # There could be more than one, from previous unfinished processes.
        # We need to figure out how to deal with that situation

        RE = re.compile(r"%s.(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).%s?$" %(self.projectname, status))
        # remember, the filename format is  yyyy-mm-dd:hh-mm-ss.<project>.<status>

        files = os.listdir(self.basedir)
        for candidate in files:
            if RE.match(candidate) is not None:
                # as soon as I find a flag, I return it. 
                self.timestamp = candidate.split('.')[1]
                self.flagfile = os.path.join(self.basedir, candidate) 
                return self.flagfile

        # if no flagfile was found...
        return None

    def clean(self):
        '''
        delete the flagfile
        '''
        os.remove(self.flagfile)

    def setstatus(self, status):
        # it would be a generic method, instead of 
        # having  setdone(), setfailed()...
        # FIXME !! TO BE IMPLEMENTED 
        pass

    def status(self):
        '''
        returns the <status> field of the flagfile
        '''
        # FIXME
        # if the class FlagFile had an attribute self.status,
        # this method would not be needed
       
        if self.flagfile:
            return self.flagfile.split('.')[-1]

        else:
            return None
 
   
    def write(self, str):
        '''
        adds content to the flagfile
        '''

        with open(self.flagfile, 'a') as flagfile:
            print >> flagfile, str
        flagfile.close()

    def read(self):
        '''
        returns the content of the flagfile
        '''
        
        flagfile = open(self.flagfile, 'r')
        content = flagfile.read()
        return content



class Project(object):
    '''
    class to keep together all actions related a Project.
    A project will typically be a VO, but not necessarily.
    Basically a project maps a single <repository> in the context of the
    file distribution tool. For example, a <repository> in CVMFS.
    Also, therefore!!, it also maps to a single UNIX ID.

    The specifications defining a project are in each section of
    the oasisprojects.conf configuration file.

    Both the class invoked by the user process -oasisCLI- 
    and  each thread created by the class invoked by the daemon process -oasisd-
    will create an object Project.
    '''

    def __init__(self, projectsection, oasisconf):
        '''
        projectsection is the section name in the oasisprojects.conf config file
        oasisconf is the ConfigParser object for oasis.conf
        '''
        #
        # !!  FIXME !!
        # pass more reasonable inputs 
        #

        # FIXME  those names 'logfile.foo' and 'console.bar' are part of the message FORMAT. Use something less ugly
        self.log = logging.getLogger('logfile.%s' %projectsection)
        self.console = logging.getLogger('console.%s' %projectsection)

        self.projectsection = projectsection
        self.oasisconf = oasisconf
        self.projectsconf = self._getprojectsconfig() 

        try:
            self.enabled = self.projectsconf.get(self.projectsection, 'enabled')
            self.username = self.projectsconf.get(self.projectsection, 'user')
            self.projectname = self.projectsconf.get(self.projectsection, 'project')
            self.vo = self._getvo()
            #self.osg_app = self._getosgapp()
            self.osg_app = self.projectsconf.get(self.projectsection, "OSG_APP")
            self.distributiontool = self.projectsconf.get(self.projectsection, 'distributiontool')
            self.srcdir = self._getsrcdir()
            self.destdir = self._getdestdir()
            self.distributionplugin = self._getdistributionplugin()
            self.oasisprobesconf = self._getprobesconfig()
            self.oasisprojectprobesconf = self._getprojectprobesconfig()
            self.sleep = self.projectsconf.getint(self.projectsection, 'time.sleep')
            self.timeout = self.projectsconf.getint(self.projectsection, 'time.timeout')
        except:
            self.log.critical('Configuration cannot be read. Aborting.')
            # FIXME !! do not exit, propagate an exception and oasisCLI or oasisd exit
            sys.exit(1)


    # =========================================================================
    #                   READ CONFIG FILES AND SETS OBJECT ATTRIBUTES
    # =========================================================================

    # -------------------------------------------------------------------------
    #                  Get the other ConfigParser objects 
    # -------------------------------------------------------------------------

    def _getprojectsconfig(self):
        '''
        gets the ConfigParser object for oasisprojects.conf
        '''
        # Maybe temporary solution
    
        oasisprojectsconffilename = self.oasisconf.get('PROJECTS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))
        return oasisprojectsconf

    def _getprobesconfig(self):
        '''
        gets the OASIS probes configurations
        '''

        oasisprobesconffilename = self.oasisconf.get('PROBES', 'oasisconf')
        oasisprobesconf = SafeConfigParser()
        oasisprobesconf.readfp(open(oasisprobesconffilename))
        return oasisprobesconf

    def _getprojectprobesconfig(self):
        '''
        gets the OASIS project probes configurations
        '''

        oasisconfigdir = self.oasisconf.get('PROBES', 'directoryconf')
        oasisprojectprobesconffilename = self.projectsconf.get(self.projectsection, 'projectprobes')
        oasisprojectprobesconf = SafeConfigParser()
        oasisprojectprobesconf.readfp(open('%s/%s' %(oasisconfigdir, oasisprojectprobesconffilename)))
        return oasisprojectprobesconf


    # -------------------------------------------------------------------------
    #                 Read variables from config object 
    # -------------------------------------------------------------------------

    def _getvo(self):
        '''
        gets the VO from the oasisprojects.conf config file.

        Reason to have a dedicated method is to allow
        the possibility that variable VO in the config file
        is not the final value and requires later interpolation.
        '''
        
        vo = self.projectsconf.get(self.projectsection, 'VO')
        # try to get VO from x509, and interpolate just in case
        #try:    
        #    st, vo = commands.getstatusoutput('voms-proxy-info -vo')
        #    if st == 0:
        #        vo_temp = string.Template(self.vo)
        #        vo = vo_temp.substitute(VO_FROM_X509, vo) 
        #except:
        #    pass

        return vo

#    def _getosgapp(self):
#
#        osg_app = self.projectsconf.get(self.projectsection, "OSG_APP")
#        # if needed, interpolate
#        osg_app_env = os.environ.get("OSG_APP", None)
#        if osg_app_env:
#            osg_app_temp = string.Template(osg_app)
#            osg_app = osg_app_temp.substitute(OSG_APP_FROM_ENV=osg_app_env)
#
#        return osg_app

    def _getsrcdir(self):
        '''
        gets the source directory from the oasisprojects.conf config file.
        It is the directory where the user payload writes.

        Reason to have a dedicated method is to allow
        the possibility that variable in the config file
        is not the final value and requires later interpolation.
        '''

        src = self.projectsconf.get(self.projectsection, "PROJECT_SRC_DIRECTORY")
        src = string.Template(src).substitute(OSG_APP=self.osg_app, VO=self.vo, project=self.projectname)
        return src

    def _getdestdir(self):
        '''
        gets the destination directory from the oasisprojects.conf config file.
        It is the directory where files are transferred for publication.

        Reason to have a dedicated method is to allow
        the possibility that variable in the config file
        is not the final value and requires later interpolation.
        '''

        dest = self.projectsconf.get(self.projectsection, "PROJECT_DEST_DIRECTORY")
        dest = string.Template(dest).substitute(VO=self.vo, project=self.projectname)
        return dest


    # -------------------------------------------------------------------------
    #                  Get the plugin for the distribution tool 
    # -------------------------------------------------------------------------

    def _getdistributionplugin(self):
        '''
        get the plugin for a given distribution tool, 
        i.e. cvmfs21
        '''

        tool = self.projectsconf.get(self.projectsection, "distributiontool")
        distribution_plugin = __import__('oasispackage.distributionplugins.%s' %tool,
                                         globals(),
                                         locals(),
                                         ['%s' %tool])

        # Always the name of the plugin and the name of the class are equal
        distribution_cls_name = tool
        distribution_cls = getattr(distribution_plugin, distribution_cls_name)
        distribution_obj = distribution_cls(self)
        return distribution_obj

    # =========================================================================
    #                   A C T I O N S    B Y     T H E    U S E R
    # =========================================================================

    def preinstall(self):
        """
        things to be done before running the user payload
        """

        rc = self._syncronize_back()
        return rc

    def _syncronize_back(self):
        """
        ensure the user scratch area has a perfect copy of what 
        is currently in the final destination area 
        """

        # FIXME temporary solution ??
        cmd = 'rsync -a -l --delete %s/ %s/' %(self.destdir, self.srcdir)
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        rc = p.returncode

        return rc


    def runpayload(self, payload):
        '''
        payload is the result of sys.argv[1:]
        For example:
           ['/var/lib/condor/execute/dir_15018/condor_exec.exe', 'a', 'b', 'c', '1', '2', '3'] 
        '''
       
        self.payload = payload
        cmd = ' '.join(self.payload)

        self.log.info('Running installation job')
        self.log.debug('Installation job path is %s' %cmd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        rc = p.returncode

        #self.log.debug('Output from installation job: %s' %out)
        self.console.info('Output from installation job: \n%s' %out)

        if rc == 0:
            self.log.info('Installation job finished OK')
        else:
            self.log.error('Installation job failed with RC=%s' %rc)

        return rc 


    def postinstall(self):
        """
        things to be done just after running the user payload
        """

        self._prepareflag()
    
        # !! FIXME !!
        return 0

    def _prepareflag(self):
        """
        prepare flag to let the daemon to know publishing is requested
        """

        # FIXME 
        #  self.flagfile = FlagFile() is done twice in this class. 
        #  do it in the __init__()
        self.flagfile = FlagFile(self.projectname)
        self.flagfile.create()
    

    # =========================================================================
    #                   A C T I O N S    B Y     T H E    D A E M O N
    # =========================================================================

    def _checkflagfile(self):
        '''
        checks if a flagfile exists for this project
        '''
        # FIXME 
        #  self.flagfile = FlagFile() is done twice in this class. 
        #  maybe it should be done in the __init__()

        self.flagfile = FlagFile(self.projectname)
        flag = self.flagfile.search('request')
        return flag

    def runprobes(self):
        '''
        run the probes.
        There are two sets of probes:
            - the generic OASIS probes, listed in oasisprobes.conf config file
            - the project specific probes, listed in oasisprobes.d/<project>.conf 

        Probes are run in a subshell, with sudo to drop privileges to the user.

        Probes code is not invoked directly. A wrapper in /usr/bin/ is run,
        and this wrapper calls the probes code.
        '''
       
        # ---------------------------------------------------------------------
        # 1st run the default OASIS probes
        # ---------------------------------------------------------------------

        self.log.debug('running probes from oasis probes config file')
        rc = self._runprobesfromconfig(self.oasisprobesconf)
        if rc != 0:
            #self.probes_rc = rc
            return rc
        self.log.debug('all probes from oasis probes config file passed OK')

        # ---------------------------------------------------------------------
        # 2nd run the specific VO probes
        # ---------------------------------------------------------------------

        self.log.debug('running probes from project %s probes config file' %self.projectsection)
        rc = self._runprobesfromconfig(self.oasisprojectprobesconf)
        if rc != 0:
            #self.probes_rc = rc
            return rc

        self.log.debug('all probes from project %s probes config file passed OK' %self.projectsection)

        # if everything went OK...
        return 0


    def _runprobesfromconfig(self, probesconf):
        '''
        run all probes from a single config file
        '''
        
        # get list of probes
        list_probes = probesconf.sections()

        for probe in list_probes:

            enabled = probesconf.getboolean(probe, 'enabled')
            probename = probesconf.get(probe, 'probe')
            level = probesconf.get(probe, 'level')
            try:
                options = probesconf.get(probe, 'options')
            except:
                options = ""

            executablename = 'oasis-runprobe-%s' %probename
            executabledir = '/usr/bin'
            executable = os.path.join(executabledir, executablename)

            if enabled:
            
                out, err, rc = self._runprobe(self.username, probe, executable, options)
   
                if rc == 0:
                    self.log.info('probe <%s> passed OK' %probe)
                else:
                    # if RC != 0, abort, but only if level is "abort"
                    if level == 'abort':
                        self.log.critical('probe <%s> failed. Aborting.' %probe)
                        return rc
                    else:
                        self.log.warning('probe <%s> failed.' %probe)
                        return 0

        # if everything went OK... 
        return 0

    def _runprobe(self, username, probe, probepath, opts):
        '''
        runs a single probe
        '''

        # create the list of input options
        # one mandatory for every probe is the root directory 
        # the rest comes from the config file
        options = '--oasisproberootdir=%s ' %self.srcdir
        options = '--oasisprobedestdir=%s ' %self.destdir
        options += opts

        cmd = 'sudo -u %s %s %s' %(username, probepath, options)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = None
        (out, err) = p.communicate()
        rc = p.returncode
        self.log.info('output of probe %s: %s' %(probe, out))
        self.flagfile.write('output of probe %s: %s\n' %(probe, out))
        return out, err, rc

    # ===========================================================================

    def transferfiles(self):
        """
        transfers files from user scratch area to final destination
        """

        rc = self.distributionplugin.transfer() 
        if rc == 0:
            self.log.info('transferring files done OK')
        else:
            self.log.critical('transferring files failed')

        return rc

    def publish(self):
        """
        publishes files once they are in the final destination
        """

        rc = self.distributionplugin.publish() 
        if rc == 0:
            self.log.info('publishing done OK')
        else:
            self.log.critical('publishing failed')

        return rc



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

    def __init__(self):

        # 
        #  !!! FIXME !!!
        #  
        # this class has some code in common with class oasisd()
        # maybe they both should inherit from a base class
        #

        self.conffile = None  # path to oasis.conf

        self.probes_rc = 0  # ?? do we need it ??

        try:
            self.oasisconf = self._getbasicconfig()
            self.username = self._getusername()
            self.projectsection = self._getprojectsection()
        except:
            self.__logerror()
            sys.exit(1)

        self._setuplogging()

        # get the Project object for that project
        try:
            self.project = Project(self.projectsection, self.oasisconf)
        except:
            self.log.critical('object Project can not be created. Aborting')
            self.console.critical('Internal OASIS malfunction. Aborting')
            sys.exit(1)


    # --------------------------------------------------------------
    #      P R E L I M I N A R I E S
    # --------------------------------------------------------------

    def __logerror(self):
        '''
        this method is just to log somehow that
        the configuration could not be read, 
        and/or an object of class Project() could not be created.
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

        # FIXME  those names 'logfile' and 'console' are part of the message FORMAT. Use something less ugly
        self.log = logging.getLogger('logfile')
        self.console = logging.getLogger('console')

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
        self.console.setLevel(logging.DEBUG)  


    # --------------------------------------------------------------

    def _getusername(self):
        '''
        get the username of whoever is calling this API
        '''
        self.log.debug('Starting.')
        
        #username = getpass.getuser()
        username = pwd.getpwuid(os.getuid()).pw_name  

        self.log.debug('Leaving with value %s.' %username)
        return username


    def _getbasicconfig(self):
        '''
        returns a ConfigParser object for oasis.conf
        the variable self.conffile is setup by the client /usr/bin/oasis
        '''
        self.log.debug('Starting.')

        oasisconf = SafeConfigParser()
        #oasisconf.readfp(open("/etc/oasis/oasis.conf"))
        oasisconf.readfp(open(self.conffile)

        self.log.debug('Leaving with value %s.' %oasisconf)
        return oasisconf


    def _getprojectsection(self):
        '''
        finds out the section in oasisprojects.conf corresponds 
        with the UNIX ID, a.k.a. self.username, running this process.
        '''
        # FIXME !! this is also done in Project() class

        self.log.debug('Starting.')

        # first get the OASIS projects ConfigFile
        oasisprojectsconffilename = self.oasisconf.get('PROJECTS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))

        # second get the section name  
        project = self.__getprojectsectionfromuser(oasisprojectsconf, self.username)
        if project:
            self.log.debug('Leaving with value %s.' %project)
            return project
        else:
            self.log.critical('Not possible to get the project section. Raising an exception.')
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

        rc = self.preinstall()
        if rc != 0:
            return rc

        rc = self.runpayload(args)
        if rc != 0:
            return rc

        rc = self.postinstall()
        if rc != 0:
            return rc

        # FIXME ?? is a while loop the best way to implement it???

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
                self.console.info('content of flagfile \n%s' %flagfile.read())
                flagfile.clean()
                return 0

            flagfilepath = flagfile.search('failed')
            if flagfilepath:
                self.console.info('content of flagfile \n%s' %flagfile.read())
                flagfile.clean()
                return 1

            # checking for timeout
            time.sleep(10)  # FIXME  why 10 ?? Should it be a config variable ??
            elapsed = time.time() - inittime
            if elapsed > self.project.timeout:
                self.log.critical('timeout. Breaking loop')
                flagfile.search('request')
                flagfile.clean() 
                return 1


        # loop is done 
        return 0


    def preinstall(self):
        rc = self.project.preinstall()
        return rc

    def runpayload(self, args):
        rc = self.project.runpayload(args)
        return rc

    def postinstall(self):
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

        self.probes_rc = 0

        self._parseopts()

        self._setuplogging()

        try:
            self.oasisconf = self._getbasicconfig()
            self.projectsconf = self._getprojectconfig()
        except:
            self.log.critical('Configuration cannot be read. Aborting.')
            sys.exit(1)


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

        oasisconf = SafeConfigParser()
        oasisconf.readfp(open(self.conffile))
        return oasisconf

    def _getprojectconfig(self):
        '''
        returns a ConfigParser object for oasisproject.conf
        '''

        oasisprojectsconffilename = self.oasisconf.get('PROJECTS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))
        return oasisprojectsconf


    # ===========================================================================

    def runthreads(self):
        """
        creates an object ProjectThreadMgr and enters main loop
        This method is intended to be called by the daemon.
        """

        try: 
            self.log.info('creating Oasis object and entering main loop')
            self.projectthreadmgr = ProjectThreadMgr(self)
            self.projectthreadmgr.mainLoop()
        except KeyboardInterrupt:
            self.log.info('Caught keyboard interrupt - exitting')
            sys.exit(0)
        #except ImportError, errorMsg:
        #    self.log.error('Failed to import necessary python module: %s' % errorMsg)
        #    sys.exit(0)
        except:
            self.log.error('Unexpected exception')
            self.log.error(traceback.format_exc(None))
            raise



# =============================================================================
#
#           P R O J E C T S      T H R E A D S 
#
# =============================================================================

class ProjectThreadMgr(object):
    '''
    this class handles the creation and destruction of threads,
    one thread per project.
    '''

    def __init__(self, oasisd):
        """
        oasisd is a reference to the class oasisd
        instantiating an object of class ProjectThreadMgr

        all threads created by this class are stored in a dictionary:
            -- key   = a Project() object
            -- value = the Thread object
            
        """

        self.log = logging.getLogger('main.projectthreadmgr')
        self.log.info('Creating object Oasis')

        self.oasisd = oasisd

        try:
            self.mainsleep = self.oasisd.oasisconf.getint('OASIS', 'time.sleep')
        except:
            # FIXME
            raise Exception 

        self.threads = {}  # dicionary to host all threads

        self.log.info("Oasis: object initialized.")


    def mainLoop(self):
        '''
        Main functional loop. 
          1. Creates all threads and starts them.
          2. Wait for a termination signal, and
             stops all threads when that happens.
        '''
        
        self.log.debug("Starting.")
        self.log.info("Starting all threads...")
        
        self.start()
       
        try:
            while True:
                time.sleep(self.mainsleep)
                self.log.debug('Checking for interrupt.')
        
        except (KeyboardInterrupt):
            logging.info("Shutdown via Ctrl-C or -INT signal.")
            self.shutdown()
            raise
        
        self.log.debug("Leaving.")

    def start(self):
        '''
        method to start all threads.
        Threads being created are stored in a dictionary.
        '''

        listprojects = self.oasisd.projectsconf.sections()
        for projectsection in listprojects:

            # create an object Project() for each section in project config 
            project = Project(projectsection, self.oasisd.oasisconf)

            if project.enabled:
                self.log.info('Project %s enabled. Creating thread' %project.projectname)
                try:

                    thread = ProjectThread(project)
                    self.threads[project] = thread
                    thread.start()
                    self.log.info('Thread for project %s started.' %project.projectname)
                except Exception, ex:
                    self.log.error('Exception captured when initializing thread for project %s.' %project.projectname)
                    self.log.debug("Exception: %s" % traceback.format_exc())
                    
            else:
                self.log.info('Project %s not enabled.' %project.projectname)


    def shutdown(self):
        '''
        Method to cleanly shut down all activity, joining threads, etc. 
        '''
    
        logging.debug(" Shutting down all threads...")
        self.log.info("Joining all threads...")

        for thread in self.threads.values():
            thread.join()

        self.log.info("All threads joined.")
        





class ProjectThread(threading.Thread):
    '''
    Each thread handles a Project() object
    '''

    def __init__(self, project):
        '''
        project is an object of class Project()
        '''

        threading.Thread.__init__(self) # init the thread

        self.log = logging.getLogger('main.projectthread[%s]' %project)
        self.log.info('Starting thread for project %s' %project)
 
        self.stopevent = threading.Event()

        self.project = project


        # recording moment the object was created
        #self.inittime = datetime.datetime.now()

        self.log.info('Thread for project %s initialized' %self.project)


    # -------------------------------------------------------------------------
    #  threading methods
    # -------------------------------------------------------------------------

    def run(self):
        '''
        Method called by thread.start()
        Main functional loop of this ProjectThread. 
            1. look for its own flag file. 
            2. run probes
            3. publish
        '''

        while not self.stopevent.isSet():
            self.log.debug("Beginning cycle in thread for Project %s" %self.project)
            try:
                # look for the flag file    
                flagfile = self.project._checkflagfile()
                if flagfile: 
                    # if flagfile exists for this project, do stuffs 
                    rc = self.project.runprobes()

                    if rc == 0:
                        self.log.info('probes ran OK, publishing')
                        rc = self.project.transferfiles()
                        if rc == 0:
                            #
                            #   !! FIXME !!
                            #   abort if transfer failed
                            #   maybe abort if publish failed
                            #   perhaps some cleaning if transfer or publish failed ??
                            self.project.publish()
                            self.project.flagfile.setdone()
                    else:
                        self.log.critical('probes failed with rc=%s, aborting installation and stopping thread' %rc)
                        self.project.flagfile.setfailed()
                        self.stopevent.set()
 
            except Exception, e:
                ms = str(e)
                self.log.error(ms)
                self.log.debug(traceback.format_exc())
            time.sleep(self.project.sleep) 
        

    def join(self,timeout=None):
        '''
        Stop the thread. 
        Overriding this method required to handle Ctrl-C from console.
        '''
    
        self.stopevent.set()
        self.log.debug('Stopping thread for Project %s...' %self.project.projectname)
        threading.Thread.join(self, timeout)
