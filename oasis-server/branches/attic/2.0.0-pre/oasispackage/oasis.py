#! /usr/bin/env python
#
#
#  Copyright (C) 2012 OSG Technology Investigation Group 
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Author: Jose Caballero

'''
    Main module for OASIS
'''

__author__ = "Jose Caballero"
__copyright__ = "2012 Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov"
__status__ = "Production"


import datetime
import logging
import logging.handlers
import threading
import time
import traceback
import os
import platform
import pwd
import socket
import sys

from pprint import pprint
from optparse import OptionParser
from ConfigParser import SafeConfigParser



major, minor, release, st, num = sys.version_info

class OASIS_CLI(object):
    """
    class to handle the command line invocation of OASIS. 
    parse the input options,
    setup everything, and run OASIS class
    """

    def __init__(self):
        self.options = None
        self.args = None
        self.log = None
        self.configloader = None

    def parseopts(self):
        parser = OptionParser()
        parser.add_option("-d", "--debug",
                          dest="logLevel",
                          default=logging.WARNING,
                          action="store_const",
                          const=logging.DEBUG,
                          help="Set logging level to DEBUG [default WARNING]")
        parser.add_option("-v", "--info",
                          dest="logLevel",
                          default=logging.WARNING,
                          action="store_const",
                          const=logging.INFO,
                          help="Set logging level to INFO [default WARNING]")
        parser.add_option("--quiet", dest="logLevel",
                          default=logging.WARNING,
                          action="store_const",
                          const=logging.WARNING,
                          help="Set logging level to WARNING [default]")
        parser.add_option("--sleep", dest="sleepTime",
                          default=120,
                          action="store",
                          type="int",
                          metavar="TIME",
                          help="Sleep TIME seconds between cycles [default %default]")
        parser.add_option("--conf", dest="confFiles",
                          default="/etc/oasis/oasis.conf",
                          action="store",
                          metavar="FILE1[,FILE2,FILE3]",
                          help="Load configuration from FILEs (comma separated list)")
        parser.add_option("--log", dest="logfile",
                          default="syslog",
                          metavar="LOGFILE",
                          action="store",
                          help="Send logging output to LOGFILE or SYSLOG [default <syslog>]")
        (self.options, self.args) = parser.parse_args()

    def setuplogging(self):
        """
        Setup logging 
        
        General principles we have tried to used for logging: 
        
        -- Logging syntax and semantics should be uniform throughout the program,  
           based on whatever organization scheme is appropriate.  
        
        -- Have at least a single log message at DEBUG at beginning and end of each function call.  
           The entry message should mention input parameters,  
           and the exit message should not any important result.  
           DEBUG output should be detailed enough that almost any logic error should become apparent.  
           It is OK if DEBUG messages are produced too fast to read interactively. 
        
        -- A moderate number of INFO messages should be logged to mark major  
           functional steps in the operation of the program,  
           e.g. when a persistent object is instantiated and initialized,  
           when a functional cycle/loop is complete.  
           It would be good if these messages note summary statistics.
           A program being run with INFO log level should provide enough output  
           that the user can watch the program function and quickly observe interesting events. 
        
        -- Initially, all logging should be directed to a single file.  
           But provision should be made for eventually directing logging output 
           from different subsystems to different files,  
           and at different levels of verbosity (DEBUG, INFO, WARN), and with different formatters.  
           Control of this distribution should use the standard Python "logging.conf" format file: 
        
        -- All messages are always printed out in the logs files, 
           but also to the stderr when DEBUG or INFO levels are selected. 
        
        -- We keep the original python levels meaning,  
           including WARNING as being the default level.  
        
                DEBUG      Detailed information, typically of interest only when diagnosing problems. 
                INFO       Confirmation that things are working as expected. 
                WARNING    An indication that something unexpected happened,  
                           or indicative of some problem in the near future (e.g. 'disk space low').  
                           The software is still working as expected. 
                ERROR      Due to a more serious problem, the software has not been able to perform some function. 
                CRITICAL   A serious error, indicating that the program itself may be unable to continue running. 
        
        Info: 
        
          http://docs.python.org/howto/logging.html#logging-advanced-tutorial  
        
        """

        self.log = logging.getLogger('main')
        if self.options.logfile == 'syslog':
            logStream = logging.handlers.SysLogHandler('/dev/log')
        else:
            lf = self.options.logfile
            logdir = os.path.dirname(lf)
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            logStream = logging.FileHandler(filename=lf)
        
        formatter = logging.Formatter('%(asctime)s (UTC) - %(name)s: %(levelname)s: %(module)s: %(message)s')
        formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
        
        self.log.setLevel(self.options.logLevel)
        self.log.debug('logging initialised')
        
    def platforminfo(self):
        '''
        display basic info about the platform, for debugging purposes 
        '''
    
        self.log.debug('platform: uname = %s %s %s %s %s %s' %platform.uname())
        self.log.debug('platform: platform = %s' %platform.platform())
        self.log.debug('platform: python version = %s' %platform.python_version())
        envmsg = ''
        for k,v in os.environ.iteritems():
            envmsg += '\n%s : %s' %(k,v)
        self.log.debug('environment : %s' %envmsg)


    def main(self):
        '''
        Creates the OASIS object and runs main loop.
        '''

        try:
            self.log.info('Creating OASIS object and entering main loop...')
            config = SafeConfigParser()
            config.readfp(open(self.options.confFiles)) 
            oasis = OASIS(config)
            oasis.main()
        except KeyboardInterrupt:
            self.log.info('Caught keyboard interrupt - exitting')
            sys.exit(0)
        #except OasisConfigurationFailure, errMsg:
        #    self.log.error('OASIS configuration failure: %s', errMsg)
        #    sys.exit(0)
        except ImportError, errorMsg:
            self.log.error('Failed to import necessary python module: %s' % errorMsg)
            sys.exit(0)
        except:
            # TODO - make this a logger.exception() call
            self.log.error('Unexpected exception that OASIS does not know how to handle.\
Please report this exception to Jose Caballero <jcaballero@bnl.gov>')
            # The following line prints the exception to the logging module
            self.log.error(traceback.format_exc(None))
            raise


class OASIS(object):
    '''
    Class implementing the main loop. 
    The class has two main goals:
            1. load the config file
            2. launch the looping thread
    '''

    def __init__(self, config):
        '''
        config is an SafeConfigParser object
        '''

        self.log = logging.getLogger('main.oasis')
        self.log.debug('OASIS: Initializing object...')
       
        # --- creating the config objects  --- 
        self.config = config
        self.tasksconf = SafeConfigParser()
        self.tasksconf.readfp(open(self.config.get('OASIS', 'tasksconf')))
        self.pluginsconf = SafeConfigParser()
        self.pluginsconf.readfp(open(self.config.get('OASIS', 'pluginsconf')))

        # --- creating a TaskManager object ---
        self.taskmanager = TaskManager(self)
        
        self.log.info("OASIS: Object initialized.")

    def main(self):
        '''
        Main functional loop of overall OASIS 
        It starts the thread implementing the ultimate loop.
        '''

        self.log.debug("main: Starting.")

        self.taskmanager.start()  # Starts all the tasks 

        try:
            while True:
                mainsleep = self.config.getint('OASIS', 'sleep')
                time.sleep(mainsleep)
                self.log.debug('Checking for interrupt.')
        
        except (KeyboardInterrupt):
            logging.info("Shutdown via Ctrl-C or -INT signal.")
            self.shutdown()
            raise
        
        self.log.debug("main: Leaving.")


    def shutdown(self):
        '''
        Method to cleanly shut down all OASIS activity, joining threads, etc. 
        '''
        self.log.debug("shutdown: Starting.")
        self.taskmanager.join()
        self.log.debug("shutdown: Leaving.")


class TaskManager(object):
    '''
    class to manage the list of tasks to be performed by this daemon. 
    '''

    def __init__(self, oasis):
        '''
        oasis is an OASIS object. 
        It is a reference to the class creating this one.
        '''

        self.log = logging.getLogger('main.taskmanager' )
        self.log.debug('TaskManager: Initializing object...')

        self.oasis = oasis 
       
        # === list of tasks  === 
        # list of task names. Each one is a section in the config file
        self.task_names = ['PublishCVMFS']
        # list of Task object. Each one corresponds to one task name
        self.tasks = []

        self.log.debug('TaskManager: Object initialized.')

    def start(self):
        '''
        starts all object Task, one per taskname in list self.task_names
        Tasks are object of a Thread class 
        '''

        self.log.debug("start: Starting")
        for taskname in self.task_names:
            self.log.info('start: Adding Task with taskname %s' %taskname)
            task = Task(taskname, self.oasis)
            self.tasks.append(task) 
            task.start() #starts the thread
        self.log.debug("start: Leaving. %d tasks initialized" %len(self.tasks))

    def join(self):
        '''    
        stops all tasks. 
        Tasks are object of a Thread class 
        '''    

        self.log.debug("join: Starting")
        for task in self.tasks:
            task.join()
        self.log.debug("join: Leaving")


class Task(threading.Thread):
    '''        
    class implementing a thread 
    for each potential task to be performed by this daemon
    '''        

    def __init__(self, taskname, oasis):
        '''
        task is the section name in the tasks config file
        oasis is an OASIS object. It is a reference to the class creating the TaskManager.
        '''

        threading.Thread.__init__(self) # init the thread
        self.log = logging.getLogger('main.task[%s]' %taskname)
        self.log.debug('Task: Initializing object Task with taskname %s' %taskname)

        self.stopevent = threading.Event()

        self.taskname = taskname
        self.oasis = oasis 
        self.config = oasis.config
        self.tasksconf = oasis.tasksconf
        self.pluginsconf = oasis.pluginsconf
       

        # there will be only two fixed configuration values for each task:
        #       - the sleep time between cycles
        #       - the plugin containing the actual taks code
        # the other potential values are meant to be consumed by the plugin 
        self.sleep = self.oasis.tasksconf.getint(self.taskname, 'sleep')
        self.pluginname = self.oasis.tasksconf.get(self.taskname, 'plugin')

        # get the plugin class and instantiate an object
        self.pluginclass = self._getplugin(self.pluginname)
        self.plugin = self.pluginclass(self)

        self.log.info("Task: Object initialized.")

    def _getplugin(self, pluginname):
        '''
        Method to create an object of the plugin class
        The plugin module will have filename <taskname>+<pluginname>.py
        The class will have the same name than the module
        '''

        self.log.debug("_getplugin: Starting" )

        modulename = pluginname
        classname = modulename
       
        self.log.debug("_getplugin: attempting to import module named %s" %modulename)

        plugin_module = __import__('oasispackage.plugins.%s' %modulename,
                                   globals(),
                                   locals(),
                                   ['%s' %modulename]) 

        self.log.debug("_getplugin: Leaving with plugin named %s" %classname)
        return getattr(plugin_module, classname)
        

    def run(self):
        ''' 
        Method called by thread.start()
        Main functional loop of this Task.
        ''' 

        self.log.debug("run: Starting" )

        while not self.stopevent.isSet():
            try:
                # call the plugin to perform the particular 
                # actions this Task is meant to do
                self.plugin.run() 
            except Exception, e:
                self.log.error("run: Caught exception: %s " % str(e))
                self.log.debug("run: Exception: %s" % traceback.format_exc())
            time.sleep(self.sleep)

        self.log.debug("run: Leaving" )

    def join(self, timeout=None):
        '''
        Stop the thread.
        Overriding this method required to handle Ctrl-C from console.
        '''

        self.log.debug("join: Starting")
        
        self.stopevent.set()
        self.log.debug('join: Stopping thread...')
        threading.Thread.join(self, timeout)
        
        self.log.debug("join: Leaving")
        
