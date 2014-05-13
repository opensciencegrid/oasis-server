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
        #
        #  !! FIXME !!
        #  Temporary implementation
        #

        self.log.info('transfering files from %s to %s' %(self.src, self.dest))

        cmd = 'rsync --stats -a -l --delete %s/ %s' %(self.project.srcdir, self.project.destdir)
        # example:   rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('transferring files failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st


    def publish(self):

        rc = self._publish()
        if rc:
            self.log.critical('publishing failed.')

        return rc

    def _publish(self):

        #
        #  !! FIXME !!
        #  Temporary implementation
        #

        self.log.info('publishing CVMFS')
        cmd = 'cvmfs_server publish'
        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('publishing failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st


    def resign(self):
        # FIXME !!!
        pass
        
    def createrepository(self):
       
        #commands.getoutput('cvmfs_server mkfs -o cvmfs oasis.opensciencegrid.org')
        os.mkdir('sudo -u cvmfs /cvmfs/oasis.opensciencegrid.org/%s' %self.project.projectname)  # ?? should I now publish ??


    def shouldlock(self, listflagfiles):
        '''
        CVMFS 2.0 should lock if there is any flagfile
        '''
    
        if listflagfiles != []:
            return True
        else:
            return False
