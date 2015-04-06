
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

# FIXME: ?? do we need a hierarchy of classes ??
# for example, cvmfs21 -> cvmfs -> BaseDistribution

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

    def abort(self):
        '''
        Does whatever is needed to leave things back as they were 
        in case of need to abort

        To be implemented by the transfer plugin.
        '''
        raise NotImplementedError
        

    def resign(self):
        '''
        when makes sense (maybe not always)
        resign the repo. 
        For example, in the case of CVMFS, resign the file .cvmfswhitelist
        '''
        raise NotImplementedError

    def createrepository(self):
        '''
        when makes sense, creates a new repository.
        '''
        raise NotImplementedError

    def createproject(self):
        '''
        when makes sense, creates a new project.
        '''
        raise NotImplementedError

    def shouldlock(self, listflagfiles):
        '''
        decides if the running process should lock and wait because
        of the presence of flagfiles or not
        '''
        raise NotImplementedError

