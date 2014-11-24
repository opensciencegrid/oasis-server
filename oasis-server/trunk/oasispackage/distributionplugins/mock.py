from oasispackage.interfaces import BaseDistribution
import  oasispackage.utils


class mock(object):

    def __init__(self, project):

        # FIXME : this is calling the root logger...
        self.log = logging.getLogger('logfile.mock')
        self.project = project


    def transfer(self):
        return 0
    
    def publish(self):
        return 0

    def resign(self):
        return 0

    def createrepository(self):
        return 0

    def createproject(self):
        return 0

    def shouldlock(self, listflagfiles):
        return False  # ???

