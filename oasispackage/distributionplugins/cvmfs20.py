#!/usr/bin/env python


import commands
import logging
import os

from oasispackage.interfaces import BaseDistribution
from oasispackage.distributionplugins.cvmfs import cvmfs

#
#  !! FIXME !!
#  Temporary implementation
#  use subprocess() instead of commands.getstatusoutput()
#


class cvmfs20(cvmfs):


    def __init__(self, project):
        super(cvmfs20, self).__init__(project)

        self.log = logging.getLogger("logfile.cvmfs20")
        self.log.debug('init of cvmfs20 plugin')

    # --------------------------------------------------------------------
    #           transfer
    # --------------------------------------------------------------------

    def transfer(self):
        """
        transfer files from user scratch area to CVMFS filesystem.
        example:   
           $ rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
           $ sudo -u ouser.atlas rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        """
        #
        # FIXME : the code here is the same of _transfer() in cvmfs21. It should go to base cvmfs.py
        #
        
        self.log.info('transfering files from %s to %s' %(self.src, self.dest))
        
        cmd = 'sudo -u %s rsync --stats -a -l --delete %s/ %s' %(self.project.project_dest_owner, self.src, self.dest)
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('transferring files failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st, out

    # --------------------------------------------------------------------
    #       publish
    # --------------------------------------------------------------------

    def publish(self):

        rc, out = self._publish()
        if rc:
            self.log.critical('publishing failed.')

        return rc, out

    def _publish(self):

        #
        #  !! FIXME !!
        #  Temporary implementation
        #  use subprocess() instead of commands.getstatusoutput()
        #

        self.log.info('publishing CVMFS')
        cmd = 'cvmfs_server publish'
        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('publishing failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st, out


    # --------------------------------------------------------------------
    #       adminstrative methods
    # --------------------------------------------------------------------

    def resign(self):
        # FIXME !!!
        pass
        

    def createrepository(self):
        '''
        create the repo area in CVMFS 2.0
        '''
        
        self.log.info('creating repository %s' %self.project.repositoryname)
        if self.checkrepository():
            self.log.info('repository %s already exists' %self.project.repositoryname)
            return 0
        else:
            rc, out = commands.getstatusoutput('cvmfs_server mkfs %s' %self.project.repositoryname)
            self.log.info('rc = %s, out=%s' %(rc,out))
            if rc != 0:
                self.log.critical('creating repository %s failed.' % self.project.repositoryname)
            return rc

    def createproject(self):
        '''
        create the project area in CVMFS 2.0
        Example:
            $ sudo -u ouser.atlas mkdir /cvmfs/oasis.opensciencegrid.org/atlas/
        '''

        self.log.info('creating project %s' %self.project.projectname)
        if self.checkproject():
            self.log.info('project %s already exists' %self.project.projectname)
            return 0
        else: 
            rc = self.createrepository()
            if rc != 0:
                self.log.critical('creating repository %s failed. Aborting.' % self.project.repositoryname)
                return rc
  
            rc, out = commands.getstatusoutput('sudo -u %s mkdir %s' %(self.project.project_dest_owner, self.dest))
            return rc


    def shouldlock(self, listflagfiles):
        '''
        CVMFS 2.0 should lock if there is any flagfile
        '''
        #FIXME
        # Maybe it should take into account if the server host is the same or not.
        # If there are more than one, then we only need to lock for projects on the same server.
    
        if listflagfiles != []:
            return True
        else:
            return False
