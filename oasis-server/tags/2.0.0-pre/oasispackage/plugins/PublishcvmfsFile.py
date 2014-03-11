#!/usr/bin/env python 


import commands
import logging
import os.path

__author__ = "Jose Caballero"
__copyright__ = "2012 Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov"
__status__ = "Development"


class PublishcvmfsFile(object):

    def __init__(self, task):
        '''
        task is an object of Task Class.
        It is a reference to the object that runs this plugin.

        This plugin searches for a file in a given path.
        If File exists, then it run the CVMFS publishing script
        and deletes the file.  
        '''

        self.log = logging.getLogger("main.publishcvmfsfile")

        self.pluginname = task.pluginname  # the name of the plugin (== name of the class)

        #self.path = task.tasksconf.get(self.taskname, 'path')
        self.pluginsconf = task.pluginsconf
        self.path = task.pluginsconf.get(self.pluginname, 'path')

        self.log.info('publishcvmfsfile: configuration variable path has value %s' %self.path)

        self.log.info('publishcvmfsfile: Object initialized.')

    def run(self):
        '''
        actual set of actions to be done by this plugin 
        '''

        self.log.debug('run: Starting.')
        if os.path.exists(self.path):
            self.log.info('run: filename %s exists. Running publish' %self.path)
            st, out = commands.getstatusoutput('/etc/cvmfs/cvmfs_publish.sh')
            self.log.info('run: CVMFS publish script finished with st=%s and out=%s' %(st, out))
            self.log.info('run: removing filename %s' %self.path)
            os.remove(self.path)
        self.log.debug('run: Leaving.')
   
