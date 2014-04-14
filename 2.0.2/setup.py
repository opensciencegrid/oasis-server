#!/usr/bin/env python
#
# Setup prog for OASIS 
#
#
release_version='2.0.2'

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


libexec_files = ['libexec/%s' %file for file in os.listdir('libexec') if os.path.isfile('libexec/%s' %file)]
oasis_etc_files = ['etc/oasisprobes.conf-example', 'etc/oasis.conf-example', 'etc/oasisusers.conf-example']
probes_etc_directory = ['etc/oasisprobes.d/%s' %file for file in os.listdir('etc/oasisprobes.d') if os.path.isfile('etc/oasisprobes.d/%s' %file) ]
condor_etc_files = ['etc/condor_oasis.conf-example',]
utils_files = ['misc/generate_adduser',
               'misc/generate_condormap',
               'misc/generate_gridmap',
              ]

# -----------------------------------------------------------

rpm_data_files=[('/usr/libexec', libexec_files),
                ('/etc/oasis', oasis_etc_files),
                ('/etc/oasis/oasisprobes.d', probes_etc_directory), 
                ('/etc/condor/config.d', condor_etc_files),
                ('/usr/share/oasis', utils_files),
               ]

# ===========================================================

# setup for distutils
setup(
    name="oasis",
    version=release_version,
    description='OASIS package',
    long_description='''This package contains OASIS''',
    license='GPL',
    author='OSG Technology Investigation Group',
    author_email='jcaballero@bnl.gov',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='http://www.opensciencegrid.org',
    packages=['oasispackage',
              'oasispackage.distributionplugins',
              'oasispackage.probesplugins',
              ],
    scripts = [ # Utilities and main script
               'bin/oasis',
               'bin/osg-oasis-update',
               'bin/osg-oasis-runprobes',
              ], 
    data_files = rpm_data_files
)
