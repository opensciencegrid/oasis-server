
import commands
import logging
import os


# -----------------------------------------------------------------------
#    Base Class (and API) for probes plugins
# -----------------------------------------------------------------------

import logging

class BaseProbe(object):

    def __init__(self, oasis, conf, section):
        """
        'oasis' is the object calling the plugins
        'conf' is a ConfigParser object with probes specs for that VO
        'section' is the section is that config object for a given probe plugin
        """

        self.log = logging.getLogger('probes')

        self.oasis = oasis
        self.conf = conf
        self.section = section

        from string import Template

        src = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_SRC_DIRECTORY")
        src = Template(src)
        self.src = src.substitute(OSG_APP=self.oasis.osg_app, VO=self.oasis.vo)

        # dest is like  /cvmfs/atlas.opensciencegrid.org
        dest = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_DEST_DIRECTORY")
        dest = Template(dest)
        self.dest = dest.substitute(VO=self.oasis.vo)


        #self.log = logging.getLogger('main.probes')

    def run(self):
       raise NotImplementedError



# -----------------------------------------------------------------------
#    Base Class (and API) for distribution plugins
# -----------------------------------------------------------------------


class BaseDistribution(object):

    def __init__(self, oasis):

        self.log = logging.getLogger('distribution')

        # oasis is the object calling this plugin
        self.oasis = oasis

        from string import Template
        
        src = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_SRC_DIRECTORY")
        src = Template(src)
        self.src = src.substitute(OSG_APP=self.oasis.osg_app, VO=self.oasis.vo)

        # dest is like  /cvmfs/atlas.opensciencegrid.org
        dest = self.oasis.oasisconf.get("DISTRIBUTION", "OASIS_VO_DEST_DIRECTORY")
        dest = Template(dest)
        self.dest = dest.substitute(VO=self.oasis.vo)

    def publish(self):
        raise NotImplementedError
