#!/usr/bin/env python 


import commands
import datetime
import logging
import os
import shutil
import subprocess
import time


#
# base class for cvmfsXY plugins
#

from oasispackage.interfaces import BaseDistribution

class cvmfs(BaseDistribution):

    def __init__(self, project):
        super(cvmfs, self).__init__(project)

        self.src = '%s/%s' %(self.project.repository_src_dir, self.project.project_src_dir)
        self.dest = '/cvmfs/%s/%s' %(self.project.repository_dest_dir, self.project.project_dest_dir)


    def checkrepository(self):
        check = os.path.isdir('/cvmfs/%s' %self.project.repositoryname)
        self.log.info('repository /cvmfs/%s exists = %s' %(self.project.repositoryname, check))
        return check

    def checkproject(self):
        check = os.path.isdir('/cvmfs/%s' %self.project.projectname)
        self.log.info('project /cvmfs/%s exists = %s' %(self.project.projectname, check))
        return check


    def synchronize_back(self):
        """
        ensure the user scratch area has a perfect copy of what 
        is currently in the final destination area 
        """

        self.log.debug('Starting.')

        # FIXME temporary solution ??
        #       maybe it should be implemented in the distribution plugin?
        #       for example, to allow easier sync from remote host
        #

        cmd = 'rsync --stats -a --delete %s/ %s/' %(self.dest, self.src)
        self.log.debug('synchronization cmd = %s' %cmd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        rc = p.returncode

        self.log.debug('Output of synchronization cmd = %s' %out)
        self.log.debug('Leaving with RC=%s' %rc)
        return rc
