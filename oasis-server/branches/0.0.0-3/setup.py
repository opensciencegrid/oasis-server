#!/usr/bin/env python
#
# Setup prog for OASIS 
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

# Python version check. 
major, minor, release, st, num = sys.version_info
if major == 2:
    if not minor >= 4:
        print("OASIS requires Python >= 2.4. Exitting.")
        sys.exit(0)

# ===========================================================
#           data files
# ===========================================================

etc_files = ['etc/tasks.conf-example',
             'etc/oasis.conf-example',
             'etc/oasis.sysconfig-example',]

libexec_files = ['libexec/condor_oasis_wrapper.sh',]

condor_config_file = ['etc/condor_oasis.conf',]

initd_files = ['etc/oasisd',]

logrotate_files = ['etc/oasis.logrotate',]

docs_files = ['docs/%s' %file for file in os.listdir('docs') if os.path.isfile('docs/%s' %file)]

# -----------------------------------------------------------

rpm_data_files=[('/usr/libexec',         libexec_files),
                ('/etc/init.d',          initd_files),
                ('/etc/oasis',           etc_files),
                ('/etc/condor/config.d', condor_config_file),
                ('/etc/logrotate.d',     logrotate_files),                                        
                ('/usr/share/doc/oasis', docs_files),                                        
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
    packages=['oasispackage', 'oasispackage.plugins','oasispackage.scripts'],
    scripts = [# utils and main script 
               'bin/oasis'
              ],
    
    data_files = rpm_data_files
)
