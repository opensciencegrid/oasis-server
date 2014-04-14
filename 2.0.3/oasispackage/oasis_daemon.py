#!/usr/bin/env python   

#
#   NOTE : temporary name
#

# 
#   NOTE : Maybe this file and oasis.py can be merged
#

import datetime
import logging
import logging.handlers
import os
import pwd
import threading
import subprocess

from ConfigParser import SafeConfigParser


class OasisdCLI(object):   # NOTE : maybe temporary name

    def __init__(self):

        self._setloggging()
        self._getconfig()

    def _setlogging(self):

        self.log = logging.getLogger()

        # set the messages format
        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASISD [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASISD [ %(levelname)s ] %(name)s : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASISD [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
            STDOUT_FORMAT='%(asctime)s (UTC) - OASISD [ %(levelname)s ] %(name)s : %(message)s'
        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        stdout_formatter = logging.Formatter(STDOUT_FORMAT)
        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
        stdout_formatter.converter = time.gmtime  # to convert timestamps to UTC

        ### adding a handler for a /var/log/ file
        logStream = logging.FileHandler('/var/log/oasis/oasisd.log')
        logStream.setFormatter(logfile_formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(logging.DEBUG)  # default

       
    def _getconfig(self): 

        self.oasisconf = SafeConfigParser().readfp(open('/etc/oasis/oasis.conf'))

        oasisprojectsconffilename = self.oasisconf.get('PROJECTS', 'projectsconf')
        self.oasisprojectsconf = SafeConfigParser().readfp(oasisprojectsconffilename)

        self.oasisprobesconffilename = self.oasisconf.get('PROBES', 'oasisconf')
        self.oasisprobesconf = SafeConfigParser().readfp(open(self.oasisprobesconffilename))

        self.oasisprobesdirconffilename = self.oasisconf.get('PROBES', 'directoryconf')


    def run(self):
        """
        create objects Oasisd and enter main loop
        """

        try: 
            self.log.info('creating Oasisd object and entering main loop')
            self.oasisd = Oasisd(self)
            self.oasisd.mainLoop()
        except KeyboardInterrupt:
            self.log.info('Caught keyboard interrupt - exitting')
            sys.exit(0)
        #except ImportError, errorMsg:
        #    self.log.error('Failed to import necessary python module: %s' % errorMsg)
        #    sys.exit(0)
        except:
            self.log.error('Unexpected exception')
            self.log.error(traceback.format_exc(None))
            raise


class Oasisd(object):

        def __init__(self, oasisdcli):
            """
            oasiscli is a reference to the class OasisdCLI
            which contains all config objects
            """

            self.log = logging.getLogger('main.oasisd')
            self.log.info('Creating object Oasisd')

            self.oasisdcli = oasisdcli

            self.threads = {}
            # to host all threads
            # key = project name (section name in oasisprojects conf file
            # value = the Thread object

            self.log.info("Oasisd: object initialized.")


        def mainLoop(self):
            '''
            Main functional loop. 
              1. Creates all threads and starts them.
              2. Wait for a termination signal, and
                 stops all threads when that happens.
            '''
            
            self.log.debug("Starting.")
            self.log.info("Starting all threads...")
            
            self.start()
           
            try:
                while True:
                    mainsleep = 30   # FIXME : This should be a config variable 
                    time.sleep(mainsleep)
                    self.log.debug('Checking for interrupt.')
            
            except (KeyboardInterrupt):
                logging.info("Shutdown via Ctrl-C or -INT signal.")
                self.shutdown()
                raise
            
            self.log.debug("Leaving.")

        def start(self):
            '''
            method to start all threads.
            '''

            listprojects = self.oasisdcli.oasisprojectsconf.keys()
            for project in listprojects:
                enabled = self.oasisdcli.oasisprojectsconf.getboolean(project,'enabled')
                if enabled:
                    self.log.info('Project %s enabled. Creating thread' %project)
                    try:
                        thread = ProjectThread(self.oasisdcli, project)
                        self.threads[project] = thread
                        thread.start()
                        self.log.info('Thread for project %s started.' %project)
                    except Exception, ex:
                        self.log.error('Exception captured when initializing thread for project %s.' %project)
                        self.log.debug("Exception: %s" % traceback.format_exc())
                        
                else:
                    self.log.info('Project %s not enabled.' %project)


        def shutdown(self):
            '''
            Method to cleanly shut down all activity, joining threads, etc. 
            '''
        
            logging.debug(" Shutting down all threads...")
            self.log.info("Joining all threads...")

            for thread in self.threads.values():
                thread.join()

            self.log.info("All threads joined.")
        

class ProjectThread(threading.Thread):

    def __init__(self, oasisdcli, project):
        '''
        oasisdcli is a reference to class OasisdCLI, 
        which contains all config object

        project is the name of the section in oasisprojects conf file
        '''

        threading.Thread.__init__(self) # init the thread

        self.log = logging.getLogger('main.projectthread[%s]' %project)
        self.log.info('Starting thread for project %s' project)
 
        self.stopevent = threading.Event()

        self.oasisdcli = oasisdcli
        self.project = project

        # recording moment the object was created
        #self.inittime = datetime.datetime.now()

        self.log.info('Thread for project %s initialized' project)


    # -------------------------------------------------------------------------
    #  threading methods
    # -------------------------------------------------------------------------

    def run(self):
        '''
        Method called by thread.start()
        Main functional loop of this ProjectThread. 
            1. look for its own flag file. 
               i.e. /var/log/oasis/<project>/job.XYZ.request or similar
            2. run probes
            3. publish
        '''

        while not self.stopevent.isSet():
            self.log.debug("Beginning cycle in thread for Project %s" %self.project)
            try:
                # look for the flag file    
                flagfile = self._flagfile()
                if flagfile: 
                    # if flagfile exists for this project, do stuffs 
                    out, rc = self.runprobes()
                    if rc == 0:
                        self.log.info('probes ran OK, publishing')
                        self.transferfiles()
                        self.publish()
                    else:
                        self.log.critical('probes failed with rc=%s and out=%s, aborting installation' %(rc, out))
                
 
            except Exception, e:
                ms = str(e)
                self.log.error(ms)
                self.log.debug(traceback.format_exc())
            time.sleep(10)
        

    def join(self,timeout=None):
        '''
        Stop the thread. 
        Overriding this method required to handle Ctrl-C from console.
        '''
    
        self.stopevent.set()
        self.log.debug('Stopping thread for Project %s...' %self.project)
        threading.Thread.join(self, timeout)
    

    # -------------------------------------------------------------------------
    #  specific methods 
    # -------------------------------------------------------------------------

    def _flagfile(self):
        '''
        checks if flagfile exists for this project
        '''
        import re

        RE = re.compile(r"flag.(\d{4})-(\d{2})-(\d{2}).request?$")

        dir = "/var/log/oasis/%s/" %self.project
        flagfiles = os.listdir(dir)
        for flag in flagfiles:
            if RE.match(file) is not None:
                self.log.info('Found a flag file for project %s' %self.project)
                return flag
        # no flag file found
        return None
        

    def runprobes(self):
        """
        invokes the code to run the probes in a subshell
        """
    
        cmd = "/usr/bin/oasis-run-probes"  # ???? or something like that
                                           # ???? maybe  "su <username>; /usr/bin/oasis-run-probes"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = None
        (out, err) = p.communicate()
        delta = time.time() - before
        log.debug('It took %s seconds to run the probes' %delta)
        if p.returncode == 0:
            log.debug('Leaving with OK return code.')
        else:
            log.warning('Leaving with bad return code. rc=%s err=%s out=%s' %(p.returncode, err, out ))
            out = None
        return (out, p.returncode)
        

    def transferfiles(self):

    def publish(self):

    
