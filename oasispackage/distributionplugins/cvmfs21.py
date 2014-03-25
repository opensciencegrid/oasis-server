#!/usr/bin/env python 


import commands
import logging
import os

from oasispackage.interfaces import BaseDistribution

class cvmfs21(BaseDistribution):


    def __init__(self, project):

        super(cvmfs21, self).__init__(project)

        #self.log = logging.getLogger("cvmfs")
        self.log.debug('init of cvmfs21 plugin')

        # self.project.dest is like  /cvmfs/myvo.opensciencegrid.org
        # the repo is the <myvo.opensciencegrid.org> part
        self.repo = self.project.destdir.split('/')[2]


    def transfer(self):

        self.log.info('transfering files from %s to %s' %(self.project.srcdir, self.project.destdir))

        ## cmd = 'cvmfs_server transaction %s' %self.repo
        # example:   cvmfs_server transaction atlas.opensciencegrid.org
        cmd = 'sudo -u oasis cvmfs_server transaction %s' %self.repo
        self.log.info('command = %s' %cmd)


        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('interaction with cvmfs server failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
            return st

        ## cmd = 'rsync -a -l --delete %s/ %s' %(self.project.srcdir, self.project.destdir)
        # example:   rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        cmd = 'sudo -u oasis rsync -a -l --delete %s/ %s' %(self.project.srcdir, self.project.destdir)
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('transferring files failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
            return st

        return st

    def publish(self):
        
        rc = self._publish()
        if rc:
            self.log.critical('publishing failed. Aborting.')
            return rc

        return 0

    def _publish(self):

        self.log.info('publishing CVMFS for repository %s' %self.repo)

        ## cmd = 'cvmfs_server publish %s' %self.repo 
        # example:   cvmfs_server publish atlas.opensciencegrid.org
        cmd = 'sudo -u oasis cvmfs_server publish %s' %self.repo 
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('publishing failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st
    
    def resign(self):
        pass 
        
