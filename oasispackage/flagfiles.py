#!/usr/bin/env python   

#
#  FIXME : temporary name
#

#
#  FIXME : 
#  getting oasis config object and projects config object 
#  is done more than once, in different __init__() methods
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
import xml.dom.minidom

from ConfigParser import SafeConfigParser

major, minor, release, st, num = sys.version_info

class FlagFile(object):
    '''
    class to handle flag files.

    flagfiles are being used in OASIS for communcation between the two main
    processes -the user process and the daemon process-:

        -- the user process creates a flagfile after running the user payload
           to request publishing

        -- the daemon starts doing tasks (run probes, transfer files, publish...)
           when it sees that flagfile

        -- the daemon changes the name of the flagfile when done

        -- daemon may write some content in the flagfile during operations,
           the user process reads it.


    The format of the flagfile is like

        yyyy-mm-dd:hh-mm-ss.<project>.<status>
   
    where status can be:

            - request
            - probes
            - done
            - failed

    Example:   2014-01-23:15:20:36.MIS.request
    
    '''

    def __init__(self, projectname):
        '''
        '''
        # FIXME ?? should I pass a Project() object ??
        # FIXME ?? should I make it without requiring any input related Projects at all ?? 
        #          For example, for FlagFileManager::search() to return a list of FlagFile objects
        #          it should be enough to pass the path to the __init__()

        self.log = logging.getLogger('logfile.flagfile')  # FIXME. The Loggers hierarchy needs to be fixed !!

        self.projectname = projectname
        # 
        # !! FIXME !!
        # Maybe read basedir from oasis.conf
        # which requires passing parent object as reference 
        # 
        self.basedir = '/var/log/oasis' 
        self.timestamp = None
        self.flagfile = None

        self.log.debug('Object created')

    def create(self):
        '''
        creates the actual file in the filesystem.
        It is created with <status> "request" as last field of the filename

        The method also gives initial value to attribute self.flagfile
        with the whole path in the filesystem to the flagfile
        '''

        self.log.debug('Starting.')

        now = time.gmtime() # gmtime() is like localtime() but in UTC
        timestr = "%04d-%02d-%02d:%02d:%02d:%02d" % (now[0], now[1], now[2], now[3], now[4], now[5])
        self.flagfile = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, timestr,  'request'))

        # FIXME !! put the open in a try-except block in case something bad happens when creating the file
        open(self.flagfile, 'w').close() 
        self.log.debug('File %s created.' %self.flagfile)

        self.log.debug('Leaving.')

    def setprobes(self):
        '''
        modifies the <status> field to 'probes'.
        Updates the self.flagfile attribute
        '''

        self.log.debug('Starting.')
        new = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, self.timestamp, 'probes'))
        os.rename(self.flagfile, new) 
        self.flagfile = new
        self.log.debug('Flagfile renamed to %s.' %self.flagfile)
        self.log.debug('Leaving.')

    def setdone(self):
        '''
        modifies the <status> field to 'done'.
        Updates the self.flagfile attribute
        '''

        self.log.debug('Starting.')
        new = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, self.timestamp, 'done'))
        os.rename(self.flagfile, new) 
        self.flagfile = new
        self.log.debug('Flagfile renamed to %s.' %self.flagfile)
        self.log.debug('Leaving.')

    def setfailed(self):
        '''
        modifies the <status> field to 'failed'.
        Updates the self.flagfile attribute
        '''

        self.log.debug('Starting.')
        new = os.path.join(self.basedir, '%s.%s.%s' %(self.projectname, self.timestamp, 'failed'))
        os.rename(self.flagfile, new) 
        self.flagfile = new
        self.log.debug('Flagfile renamed to %s.' %self.flagfile)
        self.log.debug('Leaving.')

    def search(self, status):
        '''
        searches in the filesystem for a flagfile with that particular <status>
        '''
        # !! FIXME !!
        # make it more generic, without requiring and input

        # !! FIXME !!
        # For the time being, it returns the first found file.
        # There could be more than one, from previous unfinished processes.
        # We need to figure out how to deal with that situation

        self.log.debug('Starting with status=%s' %status)

        RE = re.compile(r"%s.(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).%s?$" %(self.projectname, status))
        # remember, the filename format is  <project>.yyyy-mm-dd:hh-mm-ss.<status>

        # FIXME: use this RE
        #       RE = re.compile(r"(\S+).(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).(\S+)$" )

        files = os.listdir(self.basedir)
        for candidate in files:
            self.log.debug('Analyzing candidate file %s' %candidate)
            if RE.match(candidate) is not None:
                self.log.debug('Candidate file %s matches pattern' %candidate)
                # as soon as I find a flag, I return it. 
                self.timestamp = candidate.split('.')[1]
                self.flagfile = os.path.join(self.basedir, candidate) 
                self.log.info('Found flag file %s' %self.flagfile)
                return self.flagfile

        # ----------------------------------------------
        #  for the future
        #  instead of just returning the first flagfile
        #  found, keep of all them 
        #  (in case there is more than one)
        #  to decide what to do with them
        # ----------------------------------------------
        # list_flagfiles = []
        # files = os.listdir(self.basedir)
        # for candidate in files:
        #     if RE.match(candidate) is not None:
        #         flagfile = os.path.join(self.basedir, candidate) 
        #         list_flagfiles.append(flagfile)
        # ----------------------------------------------


        # if no flagfile was found...
        self.log.info('No flagfile found. Leaving.')
        return None

    def clean(self):
        '''
        delete the flagfile
        '''
        self.log.debug('Starting.')
        os.remove(self.flagfile)
        self.log.debug('Leaving.')

    def setstatus(self, status):
        # it would be a generic method, instead of 
        # having  setdone(), setfailed()...
        # FIXME !! TO BE IMPLEMENTED 
        pass

    def status(self):
        '''
        returns the <status> field of the flagfile
        '''
        # FIXME
        # if the class FlagFile had an attribute self.status,
        # this method would not be needed
       
        self.log.debug('Starting.')
        if self.flagfile:
            status = self.flagfile.split('.')[-1]
            self.log.debug('Returning status %s' %status)
            return status
        else:
            self.log.debug('Returning None')
            return None
 
   
    def write(self, str):
        '''
        adds content to the flagfile
        '''

        self.log.debug('Starting.')
        # FIXME !! put the writing part in a try-except block, in case something goes wrong
        flagfile = open(self.flagfile, 'a')
        print >> flagfile, str
        flagfile.close()
        self.log.debug('Leaving.')

    def read(self):
        '''
        returns the content of the flagfile
        '''
        
        self.log.debug('Starting.')
        # FIXME !! put the read part in a try-except block, in case something goes wrong
        flagfile = open(self.flagfile, 'r')
        content = flagfile.read()
        self.log.debug('Leaving returning flagfile content.')
        return content




class FlagFileManager(object):
    '''
    class to handle FlagFile objects
    '''

    def __init__(self):
        '''
        '''
        self.basedir = '/var/log/oasis' 
        self.log = logging.getLogger('logfile.flagfilemanager')  # FIXME. The Loggers hierarchy needs to be fixed !!


    def search(self, status=None):
        '''
        searches in the filesystem for any flagfile
        if status is not None, it searches for flagfiles with that value
        '''

        self.log.debug('Starting.')

        # remember, the flagfile filename format is  <project>.yyyy-mm-dd:hh-mm-ss.<status>
        if not status: 
            RE = re.compile(r"(\S+).(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).(\S+)$" )
        else:
            RE = re.compile(r"(\S+).(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).%s$" %status)

        list_flagfiles = []

        files = os.listdir(self.basedir)
        for candidate in files:
            self.log.debug('Analyzing candidate file %s' %candidate)
            if RE.match(candidate) is not None:
                self.log.debug('Candidate file %s matches pattern' %candidate)
                flagfile = os.path.join(self.basedir, candidate) 
                self.log.info('Found flag file %s' %flagfile)
                list_flagfiles.append(flagfile)

        if list_flagfiles == []:
            self.log.info('No flagfile found. Leaving.')

        return list_flagfiles 



# -------------------------------------------------------------------------
#  methods to parse the XML content of the flag file
# -------------------------------------------------------------------------

class ParseXML(object):

    def __init__(self):
        pass

    def _parseoutput(self, output):
        '''
        parses XML from flagfile content
        and creates a Python List of Dictionaries. 
        
        Input:
            <probes>
                <probe>
                    <a n="probe"><s>yes</s></a>
                    <a n="out"><s></s></a>
                    <a n="rc"><i>0</i></a>
                </probe>
                <probe>
                    <a n="probe"><s>filesize</s></a>
                    <a n="out"><s>Probe passed OK. Output of cmd "find /home/oasis/mis -size +1G -type f -exec ls -lh {} \;" was
                     
                    </s></a>
                    <a n="rc"><i>0</i></a>
                </probe>
                <probe>
                    <a n="probe"><s>yes</s></a>
                    <a n="out"><s></s></a>
                    <a n="rc"><i>0</i></a>
                </probe>
            </probes>
                
        Output:
            [
                {u'probe': 'yes', u'rc': '0'},
                {u'probe': 'filesize', u'rc': '0', u'out': 'Probe passed OK. Output of cmd "find /home/oasis/mis -size +1G -type f -exec ls -lh {} \\;" was\n         \n        '},
                {u'probe': 'yes', u'rc': '0'},
            ]
                    
        '''
        
        xmldoc = xml.dom.minidom.parseString(output).documentElement
        nodelist = []
        for probe in self._listnodesfromxml(xmldoc, 'probe') :
            node_dict = self._node2dict(probe)
            nodelist.append(node_dict)            
        return nodelist
    
    
    def _listnodesfromxml(self, xmldoc, tag):
        return xmldoc.getElementsByTagName(tag)
    
    
    def _node2dict(self, node):
        '''
        parses a node in an xml doc, as it is generated by 
        xml.dom.minidom.parseString(xml).documentElement
        and returns a dictionary with the relevant info. 
        '''
    
        dic = {}
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                key = child.attributes['n'].value
                if len(child.childNodes[0].childNodes) > 0:
                    value = child.childNodes[0].firstChild.data
                    dic[key.lower()] = str(value)
        return dic
