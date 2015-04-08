#!/usr/bin/env python   

#
#  FIXME : 
#  getting oasis config object and projects config object 
#  is done more than once, in different __init__() methods
#

#
#  FIXME : 
#  Study how I can use FlagFileManager as the only interface
#  so no part in the entire code needs to call directory FlagFile()
#  and to avoid duplicate lines between FlagFile() and FlagFileManager()
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

        yyyy-mm-dd:hh-mm-ss.<project>.<tag>
   
    where tag can be:

            - request
            - probes
            - done
            - failed

    Example:   2014-01-23:15:20:36.MIS.request
    
    '''

    def __init__(self, projectname=None, basedir=None, filename=None):
        '''
        basedir is the path of the flagfile.
        if basedir is None, then use the default /var/run/oasis

        filename can be the absolute path (basedir + filename)
        or just the actual file name
        '''

        self.log = logging.getLogger('logfile.flagfile')  # FIXME. The Loggers hierarchy needs to be fixed !!

        # !! FIXME !!
        # Maybe read basedir from oasis.conf
        # which requires passing parent object as reference 
        # 
        self.projectname = projectname
        self.basedir = '/var/run/oasis'  #default
        if basedir:
            self.basedir = basedir
        self.timestamp = None 
        self.filename = None
        self.tag = None 
        self.created = False  # says it the actual file in the filesystem has been created already or not

        # if projectname is already set, check if there is already a flagfile in the filesystem for it
        if self.projectname:
            RE = re.compile(r"%s.(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).(\S+)$" %self.projectname)
            files = os.listdir(self.basedir)
            for candidate in files:
                if RE.match(candidate) is not None:
                    self.created = True
                    self.filename = candidate
                    self.timestamp = self.filename.split('.')[1]
                    self.tag = self.filename.split('.')[2]
                    break  # we assume only one flagfile can be created per project

        # if filename is passed, check if it exists in the filesystem
        if filename:
            if os.path.isabs(filename):
                self.basedir = '/'.join(filename.split('/')[:-1])
                self.filename = filename.split('/')[-1]
            else:
                self.filename = filename
        
            self.projectname = self.filename.split('.')[0] 
            self.timestamp = self.filename.split('.')[1] 
            self.tag = self.filename.split('.')[2]

            if os.path.isfile(os.path.join(self.basedir, self.filename)):
                self.created = True

        self.log.debug('Object created')


    def create(self):
        '''
        creates the actual file in the filesystem.
        It is created with tag "request" as last field of the filename

        We assume self.projectname has a value
        '''
        # FIXME: ? should we verify that self.projectname has really a value ?
        # FIXME: ? should we verify that this FlagFile has self.created = False ?
        # FIXME !! put the open in a try-except block in case something bad happens when creating the file

        self.log.debug('Starting.')

        if self.created:
            self.log.warning('flagfile already craeted. Leaving.')
            return

        now = time.gmtime() # gmtime() is like localtime() but in UTC
        timestamp = "%04d-%02d-%02d:%02d:%02d:%02d" % (now[0], now[1], now[2], now[3], now[4], now[5])
        filename = '%s.%s.%s' %(self.projectname, timestamp,  'request')

        path = os.path.join(self.basedir, filename)
        open(path, 'w').close() 
        self.log.debug('File %s created.' %path)

        self.filename = filename
        self.timestamp = timestamp
        self.tag = 'request'
        self.created = True

        self.log.debug('Leaving.')


    def settag(self, tag):
        '''
        modifies the tag field 
        tag values = 'probes', 'done', 'failed'
        Updates the self.filename  attribute
        '''
        # FIXME: ? should we verify that this FlagFile has self.created = True ?

        self.log.debug('Starting.')

        newfilename = '%s.%s.%s' %(self.projectname, self.timestamp, tag)
        newpath = os.path.join(self.basedir, newfilename)
        oldpath = os.path.join(self.basedir, self.filename)
        os.rename(oldpath, newpath) 
        self.filename = newfilename
        self.tag = tag 

        self.log.debug('Flagfile renamed to %s.' %self.filename)
        self.log.debug('Leaving.')


    def search(self, tag):
        '''
        searches in the filesystem for a flagfile with that particular <tag>
        '''
        # !! FIXME !!
        # make it more generic, without requiring and input

        # !! FIXME !!
        # For the time being, it returns the first found file.
        # There could be more than one, from previous unfinished processes.
        # We need to figure out how to deal with that situation

        self.log.debug('Starting with tag=%s' %tag)

        ffm = FlagFileManager(basedir=self.basedir)
        list_flagfiles = ffm.search(projectname=self.projectname, tag=tag)

        if list_flagfiles == []:
            self.log.info('No flagfile found.')
        else:
            self.log.info('Found %s flagfile(s).' %len(list_flagfiles))
            
        return list_flagfiles


    def clean(self):
        '''
        delete the flagfile
        '''

        self.log.debug('Starting.')
        path = os.path.join(self.basedir, self.filename)
        os.remove(path)
        self.created = False
        self.log.debug('Leaving.')


    def write(self, str):
        '''
        adds content to the flagfile
        '''
        # FIXME !! put the writing part in a try-except block, in case something goes wrong

        self.log.debug('Starting.')

        path = os.path.join(self.basedir, self.filename)
        flagfile = open(path, 'a')
        print >> flagfile, str
        flagfile.close()

        self.log.debug('Leaving.')

    def read(self):
        '''
        returns the content of the flagfile
        '''
        # FIXME !! put the read part in a try-except block, in case something goes wrong
        
        self.log.debug('Starting.')

        path = os.path.join(self.basedir, self.filename)
        flagfile = open(path, 'r')
        content = flagfile.read()

        self.log.debug('Leaving returning flagfile content.')
        return content




class FlagFileManager(object):
    '''
    class to handle FlagFile objects
    '''

    def __init__(self, basedir=None):

        self.basedir = '/var/run/oasis' 
        if basedir:
            self.basedir = basedir

        self.log = logging.getLogger('logfile.flagfilemanager')  # FIXME. The Loggers hierarchy needs to be fixed !!


    def search(self, projectname=None, tag=None):
        '''
        searches in the filesystem for any flagfile
        if projectname is not None, it searches for flagfiles with that value
        if tag is not None, it searches for flagfiles with that value

        returns a list of FlagFile objects
        '''

        self.log.debug('Starting.')

        # remember, the flagfile filename format is  <project>.yyyy-mm-dd:hh:mm:ss.<tag>
        # we search for filenames with that format
        # depending if projectname and/or tag has values, the regexp expression can be one of these
        #   (\S+).(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).(\S+)$
        #   <projectname>.(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).(\S+)$ 
        #   (\S+).(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).<tag>$
        #   <projectname>.(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).<tag>$ 

        projstr = '(\S+)'
        if projectname:
            projstr = projectname

        tagstr = '(\S+)'
        if tag:
            tagstr = tag

        RE = re.compile(r"%s.(\d{4})-(\d{2})-(\d{2}):(\d{2}):(\d{2}):(\d{2}).%s$" %(projstr, tagstr))

        list_flagfiles = []

        files = os.listdir(self.basedir)
        for candidate in files:
            self.log.debug('Analyzing candidate file %s' %candidate)
            if RE.match(candidate) is not None:
                self.log.debug('Candidate file %s matches pattern' %candidate)
                path = os.path.join(self.basedir, candidate) 
                self.log.info('Found flag file %s' %path)
                flagfile = FlagFile(filename=path)
                list_flagfiles.append(flagfile)

        if list_flagfiles == []:
            self.log.info('No flagfile found. Leaving.')
        else:
            self.log.info('Found %s flagfile(s).' %len(list_flagfiles))


        return list_flagfiles 



# -------------------------------------------------------------------------
#  methods to parse the XML content of the flag file
# -------------------------------------------------------------------------

class FlagFileParser(object):
    """
    class with methods to parse the XML content of the flagfiles.
    It looks like this

    <data>
       <probes>
          <probe>
              <a n="probe"><s>yes</s></a>
              <a n="out"><s></s></a>
              <a n="rc"><i>0</i></a>
              <a n="inittime"><s>2014-06-25 17:01:41.692029</s></a>
              <a n="endtime"><s>2014-06-25 17:01:41.729241</s></a>
              <a n="elapsedtime"><i>0</i></a>
          </probe>
          <probe>
              <a n="probe"><s>yes</s></a>
              <a n="out"><s></s></a>
              <a n="rc"><i>0</i></a>
              <a n="inittime"><s>2014-06-25 17:01:41.732555</s></a>
              <a n="endtime"><s>2014-06-25 17:01:41.766115</s></a>
              <a n="elapsedtime"><i>0</i></a>
          </probe>
          <probe>
              <a n="probe"><s>filesize</s></a>
              <a n="out"><s>Probe passed OK. Output of cmd "find /home/oasis/mis -size +1G -type f -exec ls -lh {} \;" was
       </s></a>
              <a n="rc"><i>0</i></a>
              <a n="inittime"><s>2014-06-25 17:01:41.768658</s></a>
              <a n="endtime"><s>2014-06-25 17:01:41.805555</s></a>
              <a n="elapsedtime"><i>0</i></a>
          </probe>
       </probes>
       <transfer>
          <a n="rc"><i>256</i></a>
          <a n="out"><s>Repository whitelist is expired!</s></a>
          <a n="inittime"><s>2014-06-25 17:01:41.808788</s></a>
          <a n="endtime"><s>2014-06-25 17:01:41.864304</s></a>
          <a n="elapsedtime"><i>0</i></a>
       </transfer>
       <publish>
          <a n="rc"><i>256</i></a>
          <a n="out"><s>Repository whitelist is expired!</s></a>
          <a n="inittime"><s>2014-06-25 17:01:41.866973</s></a>
          <a n="endtime"><s>2014-06-25 17:01:41.916937</s></a>
          <a n="elapsedtime"><i>0</i></a>
       </publish>
    </data>
    """

    def __init__(self):
        pass

    def _parseoutput(self, output, tag):
        '''
        parses XML from flagfile content
        and creates a Python List of Dictionaries. 

        tag is something like "probes", "transfer", "publish"
        '''
        
        xmldoc = xml.dom.minidom.parseString(output).documentElement
        nodelist = []
        for probe in self._listnodesfromxml(xmldoc, tag) :
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
