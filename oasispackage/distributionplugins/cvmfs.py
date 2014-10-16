#!/usr/bin/env python 


import commands
import datetime
import logging
import os
import shutil
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
        check = os.path.isdir('/cvmfs/%s' %self.project.repository)
        self.log.info('repository /cvmfs/%s exists = %s' %(self.project.repository, check))
        return check

    def checkproject(self):
        check = os.path.isdir('/cvmfs/%s' %self.project.projectname)
        self.log.info('project /cvmfs/%s exists = %s' %(self.project.projectname, check))
        return check

