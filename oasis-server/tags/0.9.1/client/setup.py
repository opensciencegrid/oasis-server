#!/usr/bin/env python
#
# Setup prog for OASIS Client
#
#
release_version='0.0.9'

import commands
import os
import re
import sys

from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

# ===========================================================
#           data files
# ===========================================================

etc_files = ['etc/oasis.opensciencegrid.org.conf',
             'etc/opensciencegrid.org.conf',
            ]

pubkey = ['etc/oasis.opensciencegrid.org.pub']

#logrotate_files = ['etc/oasis.logrotate',]

#docs_files = ['docs/%s' %file for file in os.listdir('docs') if os.path.isfile('docs/%s' %file)]

# -----------------------------------------------------------

rpm_data_files=[('/etc/cvmfs/domain.d/', ['etc/opensciencegrid.org.conf'] ),
                ('/etc/cvmfs/keys/', ['etc/oasis.opensciencegrid.org.pub'] ),
                ('/etc/cvmfs/', ['etc/default.local.candidate'] ),
                #('/etc/cvmfs/config.d/', ['etc/oasis.opensciencegrid.org.conf'] ),  # seems like not needed
               ]

# ===========================================================

# setup for distutils
setup(
    name="oasis-client",
    version=release_version,
    description='OASIS Client package',
    long_description='''This package contains OASIS Client''',
    license='GPL',
    author='OSG Technology Investigation Group',
    author_email='jcaballero@bnl.gov',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='http://www.opensciencegrid.org',
    #scripts = [# utils and main script 
    #           'bin/oasis'
    #          ],
    
    data_files = rpm_data_files
)
