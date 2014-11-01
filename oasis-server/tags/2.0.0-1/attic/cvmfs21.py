#!/usr/bin/env python 


import commands
import logging
import os

from oasispackage.interfaces import BaseDistribution

class cvmfs21(BaseDistribution):

    #
    # TO DO:
    #
    #   -- log messages
    #   -- return RCs, 
    #      and abort if something went wrong
    #


    def __init__(self, oasis):

        super(cvmfs, self).__init__(oasis)

        #self.log = logging.getLogger("cvmfs")
        self.log.debug('init of cvmfs plugin')

        # self.dest is like  /cvmfs/myvo.opensciencegrid.org
        # the repo is the <myvo.opensciencegrid.org> part
        self.repo = self.dest.split('/')[2]


    def publish(self):
        
        rc = self._transfer()
        if rc:
            self.log.critical('transferring files from scratch area to destination failed. Aborting.')
            return rc

        rc = self._publish()
        if rc:
            self.log.critical('publishing failed. Aborting.')
            return rc

        return 0


    def _transfer(self):

        self.log.info('transfering files from %s to %s' %(self.src, self.dest))

        cmd = 'cvmfs_server transaction %s' %self.repo
        # example:   cvmfs_server transaction atlas.opensciencegrid.org
        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('interaction with cvmfs server failed. Aborting')
            return st

        cmd = 'rsync -a -l --delete %s/ %s' %(self.src, self.dest)
        # example:   rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        st, out = commands.getstatusoutput(cmd)
        return st


    def _publish(self):

        self.log.info('publishing CVMFS for repository %s' %self.repo)

        cmd = 'cvmfs_server publish %s' %self.repo 
        # example:   cvmfs_server publish atlas.opensciencegrid.org
        st, out = commands.getstatusoutput(cmd)
        return st

        
        
