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
        

    def createrepository(self):
        '''
        create the project area in CVMFS
        '''
        pass
        # TO BE IMPLEMENTED 


    def createproject(self):
        '''
        create the project area in CVMFS
        '''
        #rc, out = commands.getstatusoutput('sudo -u cvmfs mkdir /cvmfs/oasis.opensciencegrid.org/%s' %self.project.projectname)  # ?? should I now publish ??
        rc, out = commands.getstatusoutput('sudo -u %s mkdir /cvmfs/oasis.opensciencegrid.org/%s' %(self.project.destdiruser, self.project.projectname))
        return rc, out


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
