#!/usr/bin/env python 


import commands
import logging
import os

from oasispackage.interfaces import BaseDistribution

class cvmfs20(BaseDistribution):

    #
    # TO DO:
    #
    #   -- log messages
    #   -- return RCs, 
    #      and abort if something went wrong
    #


    #def __init__(self, oasis):
    #    super(cvmfs, self).__init__(oasis)

    def __init__(self, project):
        super(cvmfs, self).__init__(project)

        self.project = project

        #self.log = logging.getLogger("cvmfs")
        self.log.debug('init of cvmfs plugin')

        # self.dest is like  /cvmfs/myvo.opensciencegrid.org
        # the repo is the <myvo.opensciencegrid.org> part
        ##self.repo = self.dest.split('/')[2]


    def publish(self):
        
        #rc = self._transfer()
        #if rc:
        #    self.log.critical('transferring files from scratch area to destination failed. Aborting.')
        #    return rc

        rc = self._publish()
        if rc:
            self.log.critical('publishing failed.')
            return rc

        return 0


    #def _transfer(self):
    def transfer(self):

        self.log.info('transfering files from %s to %s' %(self.src, self.dest))

        ### cmd = 'cvmfs_server transaction %s' %self.repo
        ### # example:   cvmfs_server transaction atlas.opensciencegrid.org
        ### st, out = commands.getstatusoutput(cmd)
        ### if st:
        ###     self.log.critical('interaction with cvmfs server failed. Aborting')
        ###     return st

        #
        #  !! FIXME !!
        #  Temporary implementation
        #

        cmd = 'rsync -a -l --delete %s/ %s' %(self.project.srcdir, self.project.destdir)
        # example:   rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('interaction with cvmfs server failed.')
        return st


    def _publish(self):

        #
        #  !! FIXME !!
        #  Temporary implementation
        #

        self.log.info('publishing CVMFS')
        cmd = 'cvmfs_server publish'
        st, out = commands.getstatusoutput(cmd)
        return st

        
        
