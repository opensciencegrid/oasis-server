#!/usr/bin/env python


import commands
import logging
import os

from oasispackage.interfaces import BaseDistribution

class cvmfs20(BaseDistribution):


    def __init__(self, project):
        super(cvmfs20, self).__init__(project)

        self.log = logging.getLogger("logfile.cvmfs20")
        self.log.debug('init of cvmfs20 plugin')


    def transfer(self):
        #
        #  !! FIXME !!
        #  Temporary implementation
        #  use subprocess() instead of commands.getstatusoutput()
        #

        self.log.info('transfering files from %s to %s' %(self.project.srcdir, self.project.destdir))

        #cmd = 'sudo -u cvmfs rsync --stats -a -l --delete %s/ %s' %(self.project.srcdir, self.project.destdir)
        cmd = 'sudo -u %s rsync --stats -a -l --delete %s/ %s' %(self.project.destdiruser, self.project.srcdir, self.project.destdir)
        # example:   rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('transferring files failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st, out


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


    def resign(self):
        # FIXME !!!
        pass
        
    # FIXME: duplicated code in cvmfs20 and cvmfs21 !!
    def checkrepository(self):
        return os.path.isdir('/cvmfs/%s' %self.project.repository)

    # FIXME: duplicated code in cvmfs20 and cvmfs21 !!
    def checkproject(self):
        return os.path.isdir('/cvmfs/%s' %self.project.project)

    def createrepository(self):
        '''
        create the repo area in CVMFS 2.0
        '''
        
        self.log.info('creating repository %s' %self.project.repository)
        if self.checkrepository():
            self.log.info('repository %s already exists' %self.project.repository)
            return 0
        else:
            rc, out = commands.getstatusoutput('cvmfs_server mkfs %s' %self.project.repository)
            self.log.info('rc = %s, out=%s' %(rc,out))
            return rc

    def createproject(self):
        '''
        create the project area in CVMFS 2.0
        '''

        self.log.info('creating project %s' %self.project.project)
        if self.checkproject():
            self.log.info('project %s already exists' %self.project.project)
            return 0
        else: 
            self.createrepository()
  
            #rc, out = commands.getstatusoutput('sudo -u cvmfs mkdir /cvmfs/oasis.opensciencegrid.org/%s' %self.project.projectname)  # ?? should I now publish ??
            #rc, out = commands.getstatusoutput('sudo -u %s mkdir /cvmfs/oasis.opensciencegrid.org/%s' %(self.project.destdiruser, self.project.projectname))
            rc, out = commands.getstatusoutput('sudo -u %s mkdir /cvmfs/%s' %(self.project.projectuser, self.project.project))
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
