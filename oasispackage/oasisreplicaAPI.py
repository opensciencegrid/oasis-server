#!/usr/bin/env python   

#
#  FIXME : temporary name
#


import commands
import datetime
import getopt
import logging
import logging.handlers
import os
import pwd
import re
import subprocess
import string
import sys
import time
import threading
import traceback

from ConfigParser import SafeConfigParser

major, minor, release, st, num = sys.version_info



class oasisreplicad(object):
    '''
    class to be invoked by the OASIS replica daemon.
    '''

    def __init__(self):

        # FIXME
        # maybe parsing the input options should have be done already
        # in that case, the client /usr/bin/oasisd
        # would call a factory class, instead of directly class oasisd() 
        self._parseopts()

        self._setuplogging()

        try:
            self.oasisreplicaconf = self._getbasicconfig()
            oasisreplicarepositoriesconffile = self.oasisreplicaconf.get('REPLICA','repositoriesConf') 
            self.oasisreplicarepositoriesconf = SafeConfigParser()
            self.oasisreplicarepositoriesconf.readfp(open(oasisreplicarepositoriesconffile))
        except:
            self.log.critical('Configuration cannot be read. Aborting.')
            sys.exit(1)

        self.replicathreadsmanager = ReplicaThreadsManager(self)


        self.log.debug('Object oasisd created.')


    # --------------------------------------------------------------
    #      P R E L I M I N A R I E S
    # --------------------------------------------------------------

    def _parseopts(self):
        '''
        parsing the input options.
        These inputs are setup in /etc/sysconfig/oasisd.sysconfig
        '''

        opts, args = getopt.getopt(sys.argv[1:], '', ['conf=', 'loglevel=', 'logfile='])
        for o, a in opts:

            # FIXME 
            # ?? should they have default values in case they are not passed from sysconfig ??
            if o == '--conf':
                self.conffile = a

            if o == '--loglevel':
                if a == 'debug':
                    self.loglevel = logging.DEBUG
                elif a == 'info':
                    self.loglevel = logging.INFO
                elif a == 'warning':
                    self.loglevel = logging.WARNING

            if o == '--logfile':
                self.logfile = a
        

    def _setuplogging(self):
        
        self.log = logging.getLogger('oasisreplica')

        # set the messages format
        if major == 2 and minor == 4:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
        else:
            LOGFILE_FORMAT='%(asctime)s (UTC) - OASIS [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        logfile_formatter = logging.Formatter(LOGFILE_FORMAT)
        logfile_formatter.converter = time.gmtime  # to convert timestamps to UTC
       
        logStream = logging.FileHandler(self.logfile)
        logStream.setFormatter(logfile_formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(self.loglevel)  
        

    # --------------------------------------------------------------

    def _getbasicconfig(self):
        '''
        returns a ConfigParser object for oasis.conf
        '''
        self.log.debug('Start')
        oasisreplicaconf = SafeConfigParser()
        oasisreplicaconf.readfp(open(self.conffile))
        self.log.debug('Leaving with config object %s' %oasisreplicaconf)
        return oasisreplicaconf




    def run(self):
        """
        """
        self.log.debug('Start')
    
        try: 
            self.log.info('creating ReplicaThreadsManager object and entering main loop')
            self.replicathreadsmanager.update()
            self.replicathreadsmanager.run()

        except KeyboardInterrupt:
            self.log.info('Caught keyboard interrupt - exitting')
            sys.exit(0)
        except ImportError, errorMsg:
            self.log.error('Failed to import necessary python module: %s' % errorMsg)
            sys.exit(0)
        except:
            self.log.error('Unexpected exception')
            self.log.error(traceback.format_exc(None))
            raise







class ReplicaThreadsManager(object):

    def __init__(self, oasisreplicad):

        self.log = logging.getLogger('oasisreplica.replicathreadsmanager')
        self.oasisreplicad = oasisreplicad
        self.replicathreads = {}
        self.log.debug('ReplicaThreadsManager object initialized')


    def update(self):
        '''
        create all ReplicaThread objects
        '''

        for section in self.oasisreplicad.oasisreplicarepositoriesconf.sections():
            if self.oasisreplicad.oasisreplicarepositoriesconf.getboolean(repo, 'enabled'):
                replicathread = ReplicaThread(self, section)
                self.replicathreads[section] = replicathread

    def run(self):
        '''
        starts all ReplicaThread objects
        '''

        for repo, thread in self.replicathreads.iteritems():
            thread.start()


    def join(self):
        '''
        stops all ReplicaThread objects
        '''

        for repo, thread in self.replicathreads.iteritems():
            thread.join()



class ReplicaThread(threading.Thread):

    def __init__(self, replicathreadsmanager, sectionname):
    
        threading.Thread.__init__(self) # init the thread
        self.log = logging.getLogger('oasisreplica.replicathread')
        self.stopevent = threading.Event()

        self.replicathreadsmanager = replicathreadsmanager
        self.sectionname = sectionname
        self.reponame = self.replicathreadsmanager.oasisreplicad.oasisreplicarepositoriesconf.get(self.sectionname, 'repository')
        self.interval = self.replicathreadsmanager.oasisreplicad.oasisreplicarepositoriesconf.getint(self.sectionname, 'interval')
        self.ntrials = self.replicathreadsmanager.oasisreplicad.oasisreplicarepositoriesconf.getint(self.sectionname, 'ntrials')

        self.log.debug('ReplicaThread object initialized')
            

    def run(self):

        while not self.stopevent.isSet():
            self.snapshot()
            time.sleep(self.interval)

    def snapshot(self):

        self.log.info('to run snapshot for repo %s' %self.reponame)

        if os.path.isfile('/srv/cvmfs/%s/.cvmfswhitelist' %self.reponame):  # FIXME: maybe that path should be also a config variable ???

            for trial in range(self.ntrials): 

                self.log.info('attempt number %s to run snapshot on %s' %(trial+1, self.reponame))
                cmd = 'cvmfs_server snapshot %s' %self.reponame
                self.log.info('trying command %s' %cmd)
                before = time.time()
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out = None
                (out, err) = p.communicate()
                delta = time.time() - before
                self.log.info('It took %s seconds to run the snapshot for %s' %(delta, self.reponame))
                rc = p.returncode
                if rc == 0:
                    self.log.info('cmd %s succeeded with output %s' %(cmd, out))
                    break
                else:
                    self.log.error('cmd %s failed, with err %s and rc = %s' %(cmd, err, rc))
            else:
                self.log.critical('snapshot for repo %s failed after %s trials' %(self.reponame, self.ntrials))
        

    def join(self,timeout=None):
        '''
        Stop the thread. Overriding this method required to handle Ctrl-C from console.
        '''
        self.stopevent.set()
        self.log.debug('Stopping thread...')
        threading.Thread.join(self, timeout)













