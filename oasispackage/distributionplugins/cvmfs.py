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


    def checkrepository(self):
        check = os.path.isdir('/cvmfs/%s' %self.project.repository)
        self.log.info('repository /cvmfs/%s exists = %s' %(sef.project.repository, check))
        return check

    def checkproject(self):
        check = os.path.isdir('/cvmfs/%s' %self.project.projectname)
        self.log.info('project /cvmfs/%s exists = %s' %(sef.project.projectname, check))
        return check

