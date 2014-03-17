
import commands
import getopt
import logging
import os

# -----------------------------------------------------------------------
#    Base Class (and API) for probes plugins
# -----------------------------------------------------------------------


class BaseProbe(object):

    # 
    # FIXME
    # temporary solution
    # In the future, it will be a real framework:
    #       -- probes will be classes imported by the framework
    #       -- the framework will handle inputs, outputs, RCs, exceptions...
    #

    def __init__(self, options):
        """
        base class for those probes that are python code

        options is a python list, e.g. sys.argv[]
        There are two types of options 

            -- generic oasis options:
        
                -- oasisproberootdir = the src tree
                -- oasisprobedestdir = the destination tree

            -- probe specific options.
        """

        # FIXME : this is calling the root logger...
        self.log = logging.getLogger('probes') 
        self.options = options

        # start parsing the input options,
        # at least for the generic ones

        # FIXME !!
        # parsing input options maybe should not be done in the __init__()'s
        # either the base class (this one) or each probe class.
        # Consider parsing the options in the __main__ section
        opts, args = getopt.getopt(self.options, '', ['oasisproberootdir=', 'oasisprobedestdir='])
        for o, a in opts:
            if o == '--oasisproberootdir':
                self.rootdir = a
        for o, a in opts:
            if o == '--oasisprobedestdir':
                self.destdir = a

    def run(self):
       raise NotImplementedError


# -----------------------------------------------------------------------
#    Base Class (and API) for distribution plugins
# -----------------------------------------------------------------------

class BaseDistribution(object):

    def __init__(self, project):
        '''
        project is the Project() object calling this plugin
        '''

        # FIXME : this is calling the root logger...
        self.log = logging.getLogger('distribution')

        self.project = project

    def transfer(self):
        '''
        transfers files from user scratch area to final directory
        prior to publication.

        To be implemented by the transfer plugin.
        '''
        raise NotImplementedError
    
    def publish(self):
        '''
        Triggers the final publishing task.

        To be implemented by the transfer plugin.
        '''
        raise NotImplementedError





## class BaseProbe(object):
## 
##     def __init__(self, oasis, conf, section):
##         """
##         'oasis' is the object calling the plugins
##         'conf' is a ConfigParser object with probes specs for that VO
##         'section' is the section is that config object for a given probe plugin
##         """
## 
##         self.log = logging.getLogger('probes')
## 
##         self.oasis = oasis
##         self.conf = conf
##         self.section = section
## 
##         from string import Template
## 
##         src = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_SRC_DIRECTORY")
##         src = Template(src)
##         self.src = src.substitute(OSG_APP=self.oasis.osg_app, VO=self.oasis.vo)
## 
##         # dest is like  /cvmfs/atlas.opensciencegrid.org
##         dest = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_DEST_DIRECTORY")
##         dest = Template(dest)
##         self.dest = dest.substitute(VO=self.oasis.vo)
## 
## 
##         #self.log = logging.getLogger('main.probes')
## 
##     def run(self):
##        raise NotImplementedError
## 

## class BaseDistribution(object):
## 
##     def __init__(self, oasis):
## 
##         self.log = logging.getLogger('distribution')
## 
##         # oasis is the object calling this plugin
##         self.oasis = oasis
## 
##         from string import Template
##         
##         src = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_SRC_DIRECTORY")
##         src = Template(src)
##         self.src = src.substitute(OSG_APP=self.oasis.osg_app, VO=self.oasis.vo)
## 
##         # dest is like  /cvmfs/atlas.opensciencegrid.org
##         dest = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_DEST_DIRECTORY")
##         dest = Template(dest)
##         self.dest = dest.substitute(VO=self.oasis.vo)
## 
##     def publish(self):
##         raise NotImplementedError
