#!/usr/bin/env python   

#
#  FIXME : temporary name
#

#
#  FIXME : 
#  getting oasis config object and projects config object 
#  is done more than once, 
#  for example in different __init__() methods, but not only
#  Too much duplicate code. 
#

import commands
import datetime
import getopt
import logging
import logging.handlers
import os
import pwd
import re
import smtplib
import socket
import subprocess
import string
import sys
import time
import threading
import traceback

try:
    from email.mime.text import MIMEText
except:
    from email.MIMEText import MIMEText

from ConfigParser import SafeConfigParser

from oasispackage.flagfiles import FlagFile, FlagFileManager

major, minor, release, st, num = sys.version_info






class ProjectBasicConfig(object):
    '''
    class just with the basic config for a Project type object.
    No methods, just basic attributes. 
    To be inherited to add more attributes and methods,
    but can be called by clients that do not need more than the basic stuffs.
    '''

    def __init__(self, projectsection, oasisconf):
        '''
        projectsection is the section name in the projects config file
        oasisconf is the ConfigParser object for oasis.conf

        We pass oasis.conf and not the projects conf file directly 
        because we need it to get some variables from it
        '''

        # FIXME  those names 'logfile.foo' and 'user.bar' are part of the message FORMAT. Use something less ugly
        self.log = logging.getLogger('logfile.%s' %projectsection)
        self.console = logging.getLogger('user.%s' %projectsection)

        self.projectsection = projectsection
        self.oasisconf = oasisconf
        self.projectsconf = self._getprojectsconfig() 

        try:
            # !! FIXME !!
            # some variables, like VO or OSG_APP, may end up with value None
            # but then being needed for interpolation to srcdir, destdir, etc.
            # in that case, an exception should be raised, and abort
            self.enabled = self.projectsconf.get(self.projectsection, 'enabled')
            self.log.debug('variable enabled has value %s', self.enabled)

            #self.repositoryname = self.projectsconf.get(self.projectsection, 'repositoryname') 
            #self.log.debug('variable repositoryname has value %s' %self.repositoryname)  
            #self.repository_src_dir = self.projectsconf.get(self.projectsection, 'repository_src_dir') 
            #self.log.debug('variable repository_src_dir has value %s' %self.repository_src_dir)  
            #self.repository_dest_dir = self.projectsconf.get(self.projectsection, 'repository_dest_dir') 
            #self.log.debug('variable repository_dest_dir has value %s' %self.repository_dest_dir)  
            #self.repository_src_owner = self.projectsconf.get(self.projectsection, 'repository_src_owner') 
            #self.log.debug('variable repository_src_owner has value %s' %self.repository_src_owner)  
            #if self.repository_src_owner == 'root':
            #    raise Exception('repository_src_owner cannot be root')
            #self.repository_dest_owner = self.projectsconf.get(self.projectsection, 'repository_dest_owner') 
            #self.log.debug('variable repository_dest_owner has value %s' %self.repository_dest_owner)  


            # -------------------------------
            #  project configuration
            # -------------------------------

            self.projectname = self.projectsconf.get(self.projectsection, 'projectname') 
            self.log.debug('variable projectname has value %s' %self.projectname)  

            self.project_src_dir = self.projectsconf.get(self.projectsection, 'project_src_dir') 
            self.log.debug('variable project_src_dir has value %s' %self.project_src_dir)  

            self.project_dest_dir = self.projectsconf.get(self.projectsection, 'project_dest_dir') 
            self.log.debug('variable project_dest_dir has value %s' %self.project_dest_dir)  

            self.project_src_owner = self.projectsconf.get(self.projectsection, 'project_src_owner') 
            self.log.debug('variable project_src_owner has value %s' %self.project_src_owner)  
            if self.project_src_dir == 'root':
                raise Exception('project_src_dir cannot be root')
            # FIXME 
            # we keep this for compatibility (there are still old code using that variable)
            self.username = self.project_src_owner

            self.project_dest_owner = self.projectsconf.get(self.projectsection, 'project_dest_owner') 
            self.log.debug('variable project_dest_owner has value %s' %self.project_dest_owner)  

            self.sleep = self.projectsconf.getint(self.projectsection, 'sleep')
            self.log.debug('variable sleep has value %s', self.sleep)

            self.starttimeout = self.projectsconf.getint(self.projectsection, 'starttimeout')
            self.log.debug('variable starttimetime has value %s', self.starttimeout)

            self.finishtimeout = self.projectsconf.getint(self.projectsection, 'finishtimeout')
            self.log.debug('variable finishtimeout has value %s', self.finishtimeout)

            # -------------------------------
            #  repository configuration
            # -------------------------------

            self.repositoriesconffile = self.oasisconf.get('OASIS', 'repositoriesconf')
            self.repositoriesconf = SafeConfigParser()
            self.repositoriesconf.readfp(open(self.repositoriesconffile))

            self.repositorysection = self.projectsconf.get(self.projectsection, 'repositorysection')

            self.repositoryname = self.repositoriesconf.get(self.repositorysection, 'repositoryname')
            self.log.debug('variable repositoryname has value %s' %self.repositoryname)

            self.repository_src_dir = self.repositoriesconf.get(self.repositorysection, 'repository_src_dir')
            self.log.debug('variable repository_src_dir has value %s' %self.repository_src_dir)

            self.repository_dest_dir = self.repositoriesconf.get(self.repositorysection, 'repository_dest_dir')
            self.log.debug('variable repository_dest_dir has value %s' %self.repository_dest_dir)

            self.repository_src_owner = self.repositoriesconf.get(self.repositorysection, 'repository_src_owner')
            self.log.debug('variable repository_src_owner has value %s' %self.repository_src_owner)
            if self.repository_src_owner == 'root':
                # FIXME: is this the best way to do this?
                if self.project_src_dir == "":
                    # that means that the project source dir and the repository source dir are the same
                    raise Exception('repository_src_owner cannot be root')

            self.repository_dest_owner = self.repositoriesconf.get(self.repositorysection, 'repository_dest_owner')
            self.log.debug('variable repository_dest_owner has value %s' %self.repository_dest_owner)

            self.osg_app = self._getosgapp()
            #self.osg_app = self.projectsconf.get(self.projectsection, "OSG_APP")
            self.log.debug('variable osg_app has value %s', self.osg_app)

            self.distributiontool = self.repositoriesconf.get(self.repositorysection, 'distributiontool')
            self.log.debug('variable distributiontool has value %s', self.distributiontool)

            self.distributionplugin = self._getdistributionplugin()
            self.log.debug('variable distributionplugin has value %s', self.distributionplugin)

            # -------------------------------
            #  OASIS configuration
            # -------------------------------

            self.flagfilebasedir = '/var/run/oasis/'  #DEFAULT
            if self.oasisconf.has_option('OASIS', 'flagfilebasedir'):
                self.flagfilebasedir = self.oasisconf.get('OASIS', 'flagfilebasedir')
            self.log.debug('variable flagfilebasedir has value %s', self.flagfilebasedir)

            self.email = None  # DEFAULT
            if self.oasisconf.has_option('OASIS', 'email'):
                self.email = self.oasisconf.get('OASIS', 'email')
            self.log.debug('variable email has value %s', self.email)

            self.smtpserver = None  # DEFAULT
            if self.oasisconf.has_option('OASIS', 'SMTPServer'):
                self.smtpserver = self.oasisconf.get('OASIS', 'SMTPServer')
            self.log.debug('variable smtpserver has value %s', self.smtpserver)



        except Exception, ex:
            self.log.critical('Configuration cannot be read. Error message = "%s". Aborting.' %ex)
            raise ex

        self.log.debug('Object Project created.')


    def _getprojectsconfig(self):
        '''
        gets the ConfigParser object for projects conf file
        '''
        # Maybe temporary solution
    
        self.log.debug('Starting.')
        oasisprojectsconffilename = self.oasisconf.get('OASIS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))
        self.log.debug('Leaving returning config object %s.' %oasisprojectsconf)
        return oasisprojectsconf

    def _getosgapp(self):
        '''
        gets the variable OSG_APP from the projects config file.
        '''

        self.log.debug('Starting.')
        
        if self.repositoriesconf.has_option(self.repositorysection, "OSG_APP"):
            osg_app = self.repositoriesconf.get(self.repositorysection, "OSG_APP")
        else:
            self.log.warning('There is no variable OSG_APP defined in the config file')
            osg_app = None


        self.log.debug('Returning OSG_APP %s.' %osg_app)
        return osg_app

    def _getsrcdir(self):
        '''
        gets the source directory from the projects config file.
        It is the directory where the user payload writes.

        Reason to have a dedicated method is to allow
        the possibility that variable in the config file
        is not the final value and requires later interpolation.
        '''

        self.log.debug('Starting.')
        src = self.projectsconf.get(self.projectsection, "srcdir")
        # normalize, just in case
        src = os.path.normpath(src)
        self.log.debug('Returning src dir %s.' %src)
        return src

    def _getdestdir(self):
        '''
        gets the destination directory from the projects config file.
        It is the directory where files are transferred for publication.

        Reason to have a dedicated method is to allow
        the possibility that variable in the config file
        is not the final value and requires later interpolation.
        '''

        self.log.debug('Starting.')
        dest = self.projectsconf.get(self.projectsection, "destdir")
        # normalize, just in case
        dest = os.path.normpath(dest)
        self.log.debug('Returning dest dir %s.' %dest)
        return dest

    # -------------------------------------------------------------------------
    #                  Get the plugin for the distribution tool 
    # -------------------------------------------------------------------------

    # FIXME: this method is duplicated
    def _getdistributionplugin(self):
        '''
        get the plugin for a given distribution tool, 
        i.e. cvmfs21
        '''

        #tool = self.projectsconf.get(self.projectsection, "distributiontool")
        tool = self.distributiontool
        distribution_plugin = __import__('oasispackage.plugins.distribution.%s' %tool,
                                         globals(),
                                         locals(),
                                         ['%s' %tool])

        # Always the name of the plugin and the name of the class are equal
        distribution_cls_name = tool
        distribution_cls = getattr(distribution_plugin, distribution_cls_name)
        distribution_obj = distribution_cls(self)
        return distribution_obj


    # =========================================================================
    #   actions and checks related the configuration values
    # =========================================================================


    def repository(self, project=None):
        '''
        returns to which repository a given projects belongs to. 
        If not project variable is passed, then it is this one.
        '''

        if not project:
            return self.repositoryname
        else:
            for sect in self.projectsconf.sections():
                if self.projectsconf.get(sect, 'projectname') == project:
                    repositorysection = self.projectsconf.get(sect, 'repositorysection')
                    repositoryname = self.repositoriesconf.get(repositorysection, 'repositoryname')
                    return repositoryname

        # if the project is not listed in any section in the config file
        return None



class Project(ProjectBasicConfig):
    '''
    class to keep together all actions related a Project.
    A project will typically be a VO, but not necessarily.
    Basically a project maps a single <repository> in the context of the
    file distribution tool. For example, a <repository> in CVMFS.
    Also, therefore!!, it also maps to a single UNIX ID.

    The specifications defining a project are in each section of
    the projects configuration file.

    Both the class invoked by the user process -oasisCLI- 
    and  each thread created by the class invoked by the daemon process -oasisd-
    will create an object Project.
    '''

    def __init__(self, projectsection, oasisconf):
        '''
        projectsection is the section name in the projects config file
        oasisconf is the ConfigParser object for oasis.conf

        We pass oasis.conf and not projects config  directly 
        because we need it to get some variables from it
        '''
        #
        # !!  FIXME !!
        # pass more reasonable inputs:
        # instead of <project section name> and oasisconf
        # maybe it should projectname and oasisconf
        # or even projectname and projectsconf
        #
        # also, if oasisconf is only needed for one or two things, 
        # just pass them as input to __init__() directly
        #

        try:

            super(Project, self).__init__(projectsection, oasisconf)

            self.oasisprobesconf = self._getprobesconfig()
            # FIXME : maybe allow VO with no own probes, so "projectprobes" is undefined
            self.log.debug('variable oasisprobesconf has value %s', self.oasisprobesconf)

            # FIXME: allow more than one oasisproject.conf, split by comma
            # FIXME: maybe the class should be able to be instantiated without the probes conf defined. 
            #        For example, oasis-admin-addproject will not work if that config file does not exist, which is annoying.
            #        Maybe a solution could be a hierarchy of classes, 'a la java'
            self.oasisprojectprobesconf = self._getprojectprobesconfig()

            self.flagfile = FlagFile(projectname=self.projectname, basedir=self.flagfilebasedir)

            self.log.debug('variable oasisprojectprobesconf has value %s', self.oasisprojectprobesconf)

        except Exception, ex:
            self.log.critical('Configuration cannot be read. Error message = "%s". Aborting.' %ex)
            raise ex

        self.log.debug('Object Project created.')


    # =========================================================================
    #                   READ CONFIG FILES AND SETS OBJECT ATTRIBUTES
    # =========================================================================

    # -------------------------------------------------------------------------
    #                  Get the other ConfigParser objects 
    # -------------------------------------------------------------------------

    def _getprojectsconfig(self):
        '''
        gets the ConfigParser object for projects conf file
        '''
        # Maybe temporary solution
    
        self.log.debug('Starting.')
        oasisprojectsconffilename = self.oasisconf.get('OASIS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))
        self.log.debug('Leaving returning config object %s.' %oasisprojectsconf)
        return oasisprojectsconf

    def _getprobesconfig(self):
        '''
        gets the OASIS probes configurations
        '''

        self.log.debug('Starting.')
        oasisprobesconffilename = self.oasisconf.get('OASIS', 'probesconf')
        oasisprobesconf = SafeConfigParser()
        oasisprobesconf.readfp(open(oasisprobesconffilename))
        self.log.debug('Leaving returning config object %s.' %oasisprobesconf)
        return oasisprobesconf

    def _getprojectprobesconfig(self):
        '''
        gets the OASIS project probes configurations
        '''

        self.log.debug('Starting.')

        oasisprojectprobesconffilename = self.projectsconf.get(self.projectsection, 'projectprobesconf')
        oasisprojectprobesconf = SafeConfigParser()
        oasisprojectprobesconf.readfp(open(oasisprojectprobesconffilename))
        self.log.debug('Leaving returning config object %s.' %oasisprojectprobesconf)
        return oasisprojectprobesconf


    # -------------------------------------------------------------------------
    #                 Read variables from config object 
    # -------------------------------------------------------------------------

    def _getosgapp(self):
        '''
        gets the variable OSG_APP from the projects config file.
        '''

        self.log.debug('Starting.')
        
        if self.repositoriesconf.has_option(self.repositorysection, "OSG_APP"):
            osg_app = self.repositoriesconf.get(self.repositorysection, "OSG_APP")
        else:
            self.log.warning('There is no variable OSG_APP defined in the config file')
            osg_app = None


        self.log.debug('Returning OSG_APP %s.' %osg_app)
        return osg_app

    ###def _getsrcdir(self):
    ###    '''
    ###    gets the source directory from the projects config file.
    ###    It is the directory where the user payload writes.
    ###
    ###    Reason to have a dedicated method is to allow
    ###    the possibility that variable in the config file
    ###    is not the final value and requires later interpolation.
    ###    '''
    ###
    ###    self.log.debug('Starting.')
    ###    src = self.projectsconf.get(self.projectsection, "srcdir")
    ###    # normalize, just in case
    ###    src = os.path.normpath(src)
    ###    self.log.debug('Returning src dir %s.' %src)
    ###    return src
    ###
    ###def _getdestdir(self):
    ###    '''
    ###    gets the destination directory from the projects config file.
    ###    It is the directory where files are transferred for publication.
    ###
    ###    Reason to have a dedicated method is to allow
    ###    the possibility that variable in the config file
    ###    is not the final value and requires later interpolation.
    ###    '''
    ###
    ###    self.log.debug('Starting.')
    ###    dest = self.projectsconf.get(self.projectsection, "destdir")
    ###    # normalize, just in case
    ###    dest = os.path.normpath(dest)
    ###    self.log.debug('Returning dest dir %s.' %dest)
    ###    return dest


    # -------------------------------------------------------------------------
    #                  Get the plugin for the distribution tool 
    # -------------------------------------------------------------------------

    def _getdistributionplugin(self):
        '''
        get the plugin for a given distribution tool, 
        i.e. cvmfs21
        '''

        #tool = self.projectsconf.get(self.projectsection, "distributiontool")
        tool = self.distributiontool
        distribution_plugin = __import__('oasispackage.plugins.distribution.%s' %tool,
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
        self.log.debug('Starting.')
        self._set_env_osg_app()
        rc = self._synchronize_back()
        self.log.debug('Leaving with RC=%s' %rc)
        return rc

    def clean(self):
        """
        just the reverse sync part
        """
        self.log.debug('Starting.')
        rc = self._synchronize_back()
        self.log.debug('Leaving with RC=%s' %rc)
        return rc

    def _set_env_osg_app(self):
        '''
        method to add to the environment the variable OSG_APP.

        This variable may, most probably, already exist in the environment.
        However, what really matters is the value of OSG_APP in the
        OASIS config files. So, just in case, we override the value
        in the environment. 
        '''

        self.log.debug('Starting')
        if self.osg_app:
            self.log.info('Adding to environment OSG_APP = %s' %self.osg_app) 
            os.environ['OSG_APP'] = self.osg_app
        self.log.debug('Leaving')


    def _synchronize_back(self):
        return self.distributionplugin.synchronize_back()


    ###def _synchronize_back(self):
    ###    """
    ###    ensure the user scratch area has a perfect copy of what 
    ###    is currently in the final destination area 
    ###    """
    ###    self.log.debug('Starting.')

    ###    # FIXME temporary solution ??
    ###    #       maybe it should be implemented in the distribution plugin?
    ###    #       for example, to allow easier sync from remote host
    ###    #
    ###    destdir = '/cvmfs/%s/%' %(self.project.repository_dest_dir, self.project.project_dest_dir)
    ###    srcdir = '%s/%' %(self.project.repository_src_dir, self.project.project_src_dir)

    ###    cmd = 'rsync --stats -a -l --delete %s/ %s/' %(destdir, srcdir)
    ###    self.log.debug('synchronization cmd = %s' %cmd)
    ###    
    ###    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    ###    (out, err) = p.communicate()
    ###    rc = p.returncode

    ###    self.log.debug('Output of synchronization cmd = %s' %out)
    ###    self.log.debug('Leaving with RC=%s' %rc)
    ###    return rc


    def runpayload(self, payload):
        '''
        #payload is the result of sys.argv[1:]
        #For example:
        #   ['/var/lib/condor/execute/dir_15018/condor_exec.exe', 'a', 'b', 'c', '1', '2', '3'] 

        payload is the result of join sys.argv[1:]
        For example:
           '/var/lib/condor/execute/dir_15018/condor_exec.exe a b c 1 2 3' 
        '''
        self.log.debug('Starting.')
       
        self.payload = payload
        #cmd = ' '.join(self.payload)
        cmd = self.payload

        self.log.info('Running installation job')
        self.console.info('Running installation job')
        self.log.debug('Installation job path is %s' %cmd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        rc = p.returncode

        #self.log.debug('Output from installation job: %s' %out)
        self.console.info('Output from installation job: \n%s' %out)

        if rc == 0:
            self.log.info('Installation job finished OK')
            self.console.info('Installation job finished OK')
        else:
            self.log.error('Installation job failed with RC=%s' %rc)
            self.console.error('Installation job failed with RC=%s' %rc)

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

        self.log.debug('Starting.')

        # FIXME 
        #  self.flagfile = FlagFile() is done twice in this class. 
        #  do it in the __init__()
        ###self.flagfile = FlagFile(self.projectname)
        self.flagfile.create()

        self.log.debug('Leaving.')
    

    # =========================================================================
    #                   A C T I O N S    B Y     T H E    D A E M O N
    # =========================================================================

    ## BEGIN TEST ##
    #def _checkflagfile(self):
    #    '''
    #    checks if a flagfile exists for this project
    #    and if its tag is request
    #    '''
    #
    #    self.log.debug('Starting.')
    #
    #    ffm = FlagFileManager(self.flagfilebasedir) 
    #    flagfiles = ffm.search(projectname=self.projectname)
    #    self.log.debug('found %s flagfiles total' %len(flagfiles))
    #
    #    if flagfiles == []:
    #        self.log.debug('No flagfile found') 
    #        return False
    #    else:
    #        # we assume there is only 1 flagfile per project at a time
    #        self.log.debug('Found flagfile %s' %flagfiles[0].filename)
    #        if flagfiles[0].tag == 'request':
    #            self.log.debug('tag for found flagfile is "request". Return True')
    #            return True
    #        else:
    #            self.log.debug('tag for found flagfile is not "request". Return False')
    #            return False 
    def _checkflagfile(self):
        '''
        checks if a flagfile exists for this project
        and if its tag is request
        '''

        self.log.debug('Starting.')

        flagfiles = ffm.search(projectname=self.projectname)
        if flagfiles == []:
            self.log.debug('No flagfile found for this project')
            return False

        ffm = FlagFileManager(self.flagfilebasedir)
        flagfiles = ffm.search(tag='request')

        self.log.debug('found %s flagfiles total' %len(flagfiles))

        if flagfiles == []:
            self.log.debug('No flagfile found')
            return False
        else:

            shouldlock = self.distributionplugin.shouldlock(flagfiles)
            self.log.debug('distribution plugin method shouldlock returned %s' %shouldlock)
            return not shouldlock

    ## BEGIN TEST ##


    def runprobes(self):
        '''
        run the probes.
        There are two sets of probes:
            - the generic OASIS probes, listed in oasisprobes.conf config file
            - the project specific probes

        Probes are run in a subshell, with sudo to drop privileges to the user.

        Probes code is not invoked directly. A wrapper in /usr/bin/ is run,
        and this wrapper calls the probes code.
        '''

        #
        # !! FIXME !!
        # there is a lot of duplicated lines
        # this should be implemented in two classes:
        #       -- class Probe()
        #       -- class ProbesManager()
        #
       
         
        inittime = datetime.datetime.now()

        #
        # FIXME !!
        # maybe this method should not add content to XML flagfile
        # maybe it should return a python object with all info
        # at let the ProjectThread::run method to fill the flagfile
        #
        # FIXME
        # do not write the XML like that.
        # we should use a python library to handle XML.
        #

        self.flagfile.write('<data>')
        self.flagfile.write('<probes>')
       
        # ---------------------------------------------------------------------
        # 1st run the specific VO probes
        # ---------------------------------------------------------------------
        self.log.debug('running probes from project %s probes config file' %self.projectsection)
        rc = self._runprobesfromconfig(self.oasisprojectprobesconf)
        if rc != 0:
            self.log.critical('running probes from project %s probes config file failed' %self.projectsection)
            #self.probes_rc = rc

            #
            # FIXME !!
            # maybe this method should not add content to XML flagfile
            # maybe it should return a python object with all info
            # at let the ProjectThread::run method to fill the flagfile
            #
            # FIXME
            # do not write the XML like that.
            # we should use a python library to handle XML.
            #

            self.flagfile.write('</probes>')
            return rc
        self.log.info('all probes from project %s probes config file passed OK' %self.projectsection)

        # ---------------------------------------------------------------------
        # 2nd run the default OASIS probes
        #   we run OASIS probes after in case some VO probe creates 
        #   a file too large or something like that
        # ---------------------------------------------------------------------
        self.log.debug('running probes from oasis probes config file')
        rc = self._runprobesfromconfig(self.oasisprobesconf)
        if rc != 0:
            self.log.critical('running probes from oasis probes config file failed')
            #self.probes_rc = rc 

            #
            # FIXME !!
            # maybe this method should not add content to XML flagfile
            # maybe it should return a python object with all info
            # at let the ProjectThread::run method to fill the flagfile
            #
            # FIXME
            # do not write the XML like that.
            # we should use a python library to handle XML.
            #
            self.flagfile.write('</probes>')

            return rc
        self.log.info('all probes from oasis probes config file passed OK')

        delta = datetime.datetime.now() - inittime

        self.log.debug('time to run probes: %s seconds' %(delta.days*24*3600 + delta.seconds))

        # if everything went OK...

        #
        # FIXME !!
        # maybe this method should not add content to XML flagfile
        # maybe it should return a python object with all info
        # at let the ProjectThread::run method to fill the flagfile
        #
        # FIXME
        # do not write the XML like that.
        # we should use a python library to handle XML.
        #
        self.flagfile.write('</probes>')
        return 0


    def _runprobesfromconfig(self, probesconf):
        '''
        run all probes from a single config file
        '''
        self.log.debug('Starting for probesconf = %s' %probesconf)
         
        # get list of probes
        list_probes = probesconf.sections()

        for probe in list_probes:
            self.log.debug('candidate probe %s' %probe)
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
                self.log.debug('candidate probe %s is enabled' %probe) 

                out, err, rc = self._runprobe(self.project_src_owner, probe, executable, options)
                self.log.info('Output of probe %s was\n%s' %(probe, out))
                self.log.info('Error of probe %s was\n%s' %(probe, err))
                self.log.info('RC of probe %s was %s' %(probe, rc))
   
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
        self.log.debug('Leaving')
        return 0

    def _runprobe(self, username, probe, probepath, opts):
        '''
        runs a single probe
        '''
        self.log.debug('Starting')

        # create the list of input options
        # one mandatory for every probe is the root directory 
        # the rest comes from the config file
        options = '--oasisproberootdir=%s ' %self.distributionplugin.src
        options += '--oasisprobedestdir=%s ' %self.distributionplugin.dest
        options += opts
        
        # if user is root (this process is run by the daemon)
        #       call the probes with sudo to drop privileges
        # if the user is a regular user (this process is run from CLI by the user directly)
        #       call the probes normally 

        if os.getuid() == 0:
            ###cmd = 'sudo -u %s %s %s' %(username, probepath, options)
            cmd = 'runuser -s /bin/bash %s -c "%s %s"' %(username, probepath, options)
        else:
            cmd = '%s %s' %(probepath, options)
        self.log.info('command to run probe is "%s"' %cmd)

        inittime = datetime.datetime.now()
        self.log.info('running probe start at %s' %inittime)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = None
        (out, err) = p.communicate()
        rc = p.returncode

        endtime = datetime.datetime.now()
        self.log.info('running probe end at %s' %endtime)
        delta = endtime - inittime
        deltaseconds = delta.days*24*3600 + delta.seconds

        self.log.info('output of probe %s: %s' %(probe, out))

        # FIXME
        # do not write the XML like that.
        # we should use a python library to handle XML.
        #
        #self.flagfile.write('output of probe %s: %s\n' %(probe, out))
        self.flagfile.write('   <probe>')
        self.flagfile.write('       <a n="probe"><s>%s</s></a>' %probe)
        self.flagfile.write('       <a n="out"><s>%s</s></a>' %out)
        self.flagfile.write('       <a n="rc"><i>%d</i></a>' %rc)
        self.flagfile.write('       <a n="inittime"><s>%s</s></a>' %inittime)
        self.flagfile.write('       <a n="endtime"><s>%s</s></a>' %endtime)
        self.flagfile.write('       <a n="elapsedtime"><i>%d</i></a>' %deltaseconds)
        self.flagfile.write('   </probe>')


        self.log.debug('Leaving.')
        return out, err, rc

    # ===========================================================================

    def transferfiles(self):
        """
        transfers files from user scratch area to final destination
        """
        self.log.debug('Starting')

        inittime = datetime.datetime.now()
        self.log.info('transferfiles start at %s' %inittime)
        # FIXME 
        # maybe it should return RC and some err message when failed
        rc, out = self.distributionplugin.transfer() 

        endtime = datetime.datetime.now()
        self.log.info('transferfiles end at %s' %endtime)
        delta = endtime - inittime
        deltaseconds = delta.days*24*3600 + delta.seconds


        if rc == 0:
            self.log.info('transferring files done OK')
            self.log.debug('time to transfer files: %s seconds' %deltaseconds)
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            msg = '%s (UTC) : transfer files operation failed for project  %s' %(timestamp, self.project.projectname)
            self.emailalert(msg)
            self.log.critical('transferring files failed. RC=%s, out=%s' %(rc, out))


        #
        # FIXME !!
        # maybe this method should not add content to XML flagfile
        # maybe it should return a python object with all info
        # at let the ProjectThread::run method to fill the flagfile
        #
        # FIXME
        # do not write the XML like that.
        # we should use a python library to handle XML.
        #
        self.flagfile.write('<transfer>')
        self.flagfile.write('   <a n="rc"><i>%d</i></a>' %rc)
        self.flagfile.write('   <a n="out"><s>%s</s></a>' %out)
        self.flagfile.write('   <a n="inittime"><s>%s</s></a>' %inittime)
        self.flagfile.write('   <a n="endtime"><s>%s</s></a>' %endtime)
        self.flagfile.write('   <a n="elapsedtime"><i>%d</i></a>' %deltaseconds)
        self.flagfile.write('</transfer>')


        self.log.debug('Leaving with rc %s' %rc)
        return rc

    def publish(self):
        """
        publishes files once they are in the final destination
        """
        self.log.debug('Starting')

        inittime = datetime.datetime.now()
        self.log.info('publish start at %s' %inittime)
        # FIXME 
        # maybe it should return RC and some err message when failed
        rc, out = self.distributionplugin.publish() 

        endtime = datetime.datetime.now()
        self.log.info('publish end at %s' %endtime)
        delta = endtime - inittime
        deltaseconds = delta.days*24*3600 + delta.seconds


        if rc == 0:
            self.log.info('publishing done OK')
            self.log.debug('time to publish: %s seconds' %deltaseconds)
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            msg = '%s (UTC) : publish operation failed for project %s' %(timestamp, self.project.projectname)
            self.emailalert(msg)
            self.log.critical('publishing failed. RC=%s, out=%s' %(rc, out))


        #
        # FIXME !!
        # maybe this method should not add content to XML flagfile
        # maybe it should return a python object with all info
        # at let the ProjectThread::run method to fill the flagfile
        #
        # FIXME
        # do not write the XML like that.
        # we should use a python library to handle XML.
        #
        self.flagfile.write('<publish>')
        self.flagfile.write('   <a n="rc"><i>%d</i></a>' %rc)
        self.flagfile.write('   <a n="out"><s>%s</s></a>' %out)
        self.flagfile.write('   <a n="inittime"><s>%s</s></a>' %inittime)
        self.flagfile.write('   <a n="endtime"><s>%s</s></a>' %endtime)
        self.flagfile.write('   <a n="elapsedtime"><i>%d</i></a>' %deltaseconds)
        self.flagfile.write('</publish>')

        self.log.debug('Leaving with rc %s' %rc)
        return rc


    def emailalert(self, msg):
        '''
        sent notifications by email
        '''
        # FIXME: should this be in oasisAPI.py ???

        if self.email and self.smtpserver:

            username = pwd.getpwuid(os.getuid()).pw_name
            hostname = socket.gethostname()

            msg = MIMEText(msg)
            msg['Subject'] = 'ALERT FROM OASIS: CRITICAL OPERATION FAILED'
            email_from = "%s@%s" % (username, hostname)
            msg['From'] = email_from
            msg['To'] = self.email
            tolist = self.adminemail.split(",")

            # Send the message via our own SMTP server, but don't include the
            # envelope header.
            s = smtplib.SMTP(self.smtpserver)
            self.log.info("Sending email: %s" % msg.as_string())
            s.sendmail(email_from , tolist , msg.as_string())
            s.quit()

    
      




class ProjectFactory(object):
    # VERY IMPORTANT
    # This class must be placed in the code after the classes Project, ProjectBasicConfig...
    # because otherwise the clstype is unknown when used.
    '''
    class to create objects Project passing different types of inputs
    '''

    # FIXME maybe projectname, projectsection should be passed to getProject() call instead of __init__()
    def __init__(self, oasisconf='/etc/oasis/oasis.conf', clstype=Project, username=None, projectname=None, projectsection=None):
        self.clstype = clstype
        self.oasisconf = oasisconf
        self.username = username
        self.projectname = projectname
        self.projectsection = projectsection
    
    def getProject(self):
        # FIXME: find out how to make 2nd step better instead of using strings.
    
        # 1st, we get the right projectsection
        if self.username:
            projectsection = self._getprojectsectionfromusername(self.username)
    
        if self.projectname:
            projectsection = self._getprojectsectionfromprojectname(self.projectname)

        # 2nd, we return one of the object Factory*() 
        try:
            projectobj = self.clstype(projectsection, self.oasisconf)
            return projectobj
        except Exception, ex:
            raise ex

    
    def _getprojectsectionfromusername(self, username):
    
        # first get the OASIS projects ConfigFile
        oasisprojectsconffilename = self.oasisconf.get('OASIS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))

        # second get the section name  
        for section in oasisprojectsconf.sections():
            if oasisprojectsconf.get(section, 'user') == username:
                return section
        return None
    
    def _getprojectsectionfromprojectname(self, projectname):
    
        # first get the OASIS projects ConfigFile
        oasisprojectsconffilename = self.oasisconf.get('OASIS', 'projectsconf')
        oasisprojectsconf = SafeConfigParser()
        oasisprojectsconf.readfp(open(oasisprojectsconffilename))

        # second get the section name  
        for section in oasisprojectsconf.sections():
            if oasisprojectsconf.get(section, 'project') == projectname:
                return section
        return None
    



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
        self.log.info('Creating object ProjectThreadMgr')

        self.oasisd = oasisd

        try:
            self.mainsleep = self.oasisd.oasisconf.getint('OASIS', 'sleep')
        except:
            # FIXME
            raise Exception 

        self.threads = {}  # dicionary to host all threads

        self.log.info("Object ProjectThreadMgr initialized.")


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
        self.log.debug('Start')

        listprojects = self.oasisd.projectsconf.sections()
        for projectsection in listprojects:

            # create an object Project() for each section in project config 
            self.log.info('Candidate for a project in project section %s' %projectsection)
            self.log.info('Creating object Project')

            try:
                project = Project(projectsection, self.oasisd.oasisconf)
                # FIXME: use ProjectFactory()

                if project.enabled:
                    self.log.info('Project %s is enabled. Creating thread' %project.projectname)
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
            except Exception, ex:
                self.log.error('project object cannot be created. Error message = "%s"' %ex)


        self.log.debug('Leaving')


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

        self.log = logging.getLogger('main.projectthread[%s]' %project.projectname)
        self.log.info('Starting thread for project %s' %project.projectname)
 
        self.stopevent = threading.Event()

        self.project = project

        self.log.info('Thread for project %s initialized' %self.project.projectname)


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
                if self.project._checkflagfile():
                    # if flagfile exists for this project, and its tag is "request", do stuffs 

                    #
                    # !!! FIXME  !!!
                    # 
                    # write the algorithm in a cleaner way,
                    # instead of 3 leves of if-else blocks
                    #

                    # ------------------------------------
                    #   run probes
                    # ------------------------------------
                    self.log.info('Starting to run probes')
                    #self.console.info('Starting to run probes')
                    rc = self.project.runprobes()
                    if rc != 0:
                        self.log.critical('probes failed with rc=%s, aborting installation ' %rc)
                        #self.console.critical('probes failed with rc=%s, aborting installation and stopping thread' %rc)

                        #
                        # FIXME !!
                        # maybe this method should not add content to XML flagfile
                        # maybe it should return a python object with all info
                        # at let the ProjectThread::run method to fill the flagfile
                        # FIXME
                        # do not write the XML like that.
                        # we should use a python library to handle XML.
                        #
                        #
                        self.project.flagfile.write('</data>')
                        self.project.flagfile.settag('failed')
                    else:
                        self.log.info('probes ran OK')
                        #self.console.info('probes ran OK')

                        # ------------------------------------
                        #   transfer files 
                        # ------------------------------------
                        self.log.info('Starting to transfer files')
                        #self.console.info('Starting to transfer files')
                        rc = self.project.transferfiles()
                        if rc != 0:
                            self.log.critical('transferring files failed with rc=%s, aborting installation' %rc)
                            #self.console.critical('transferring files failed with rc=%s, aborting installation and stopping thread' %rc)

                            #
                            # FIXME !!
                            # maybe this method should not add content to XML flagfile
                            # maybe it should return a python object with all info
                            # at let the ProjectThread::run method to fill the flagfile
                            #
                            # FIXME
                            # do not write the XML like that.
                            # we should use a python library to handle XML.
                            #
                            self.project.flagfile.write('</data>')
                            self.project.flagfile.settag('failed')
                        else:
                            self.log.info('files transferred OK')
                            #self.console.info('files transferred OK')

                            # ------------------------------------
                            #   publish 
                            # ------------------------------------
                            self.log.info('Starting to publish files')
                            #self.console.info('Starting to publish files')
                            rc = self.project.publish()
                            if rc == 0:
                                self.log.info('publishing done OK')
                                #self.console.info('publishing done OK')

                                #
                                # FIXME !!
                                # maybe this method should not add content to XML flagfile
                                # maybe it should return a python object with all info
                                # at let the ProjectThread::run method to fill the flagfile
                                #
                                # FIXME
                                # do not write the XML like that.
                                # we should use a python library to handle XML.
                                #
                                self.project.flagfile.write('</data>')
                                self.project.flagfile.settag('done')
                            else:
                                self.log.critical('publishing failed with rc=%s, aborting installation' %rc)
                                #self.console.critical('publishing failed with rc=%s, aborting installation and stopping thread' %rc)

                                #
                                # FIXME !!
                                # maybe this method should not add content to XML flagfile
                                # maybe it should return a python object with all info
                                # at let the ProjectThread::run method to fill the flagfile
                                #
                                # FIXME
                                # do not write the XML like that.
                                # we should use a python library to handle XML.
                                #
                                self.project.flagfile.write('</data>')
                                self.project.flagfile.settag('failed')

 
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
        self.log.debug('Start')    
        self.stopevent.set()
        self.log.info('Stopping thread for Project %s...' %self.project.projectname)
        threading.Thread.join(self, timeout)
        self.log.debug('All threads stop. Leaving')    



