from oasispackage.interfaces import BaseDistribution
from oasispackage.distributionplugins.cvmfs import cvmfs
import  oasispackage.utils


class mock(object):

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

