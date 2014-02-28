#!/usr/bin/env python 


import commands
import logging
import os

from oasispackage.interfaces import BaseDistribution

class cvmfs20(BaseDistribution):


    def __init__(self, project):
        super(cvmfs20, self).__init__(project)

        #self.log = logging.getLogger("cvmfs")
        self.log.debug('init of cvmfs20 plugin')


    def transfer(self):
        """
        """

        self.log.info('transfering files from %s to %s' %(self.src, self.dest))

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

    def publish(self):
        """
        """

        rc = self._publish()
        if rc:
            self.log.critical('publishing failed.')

        return rc

    def _publish(self):
        """
        """

        #
        #  !! FIXME !!
        #  Temporary implementation
        #

        self.log.info('publishing CVMFS')
        cmd = 'cvmfs_server publish'
        st, out = commands.getstatusoutput(cmd)
        return st

        
        
