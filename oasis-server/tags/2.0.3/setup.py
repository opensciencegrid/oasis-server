#!/usr/bin/env python
#
# Setup prog for OASIS 
#
#
release_version='2.0.3'

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

utils_files = ['misc/generate_adduser',
               'misc/generate_condormap',
               'misc/generate_gridmap',
              ]

initd_files = ['etc/oasisd']

# =============================
#    admin tools 
# =============================
sbin_files = ['sbin/oasis-admin-projectadd',
              'sbin/oasis-admin-start',
              'sbin/oasis-admin-restart',
              'sbin/oasis-admin-stop',
              'sbin/oasis-admin-status',
             ]

# -----------------------------------------------------------

rpm_data_files=[('/usr/libexec', libexec_files),
                ('/usr/share/oasis', utils_files),
                ('/etc/init.d', initd_files),
                ('/usr/sbin', sbin_files),
               ]

# ===========================================================

# setup for distutils
setup(
    name="oasis",
    version=release_version,
    description='OASIS package',
    long_description='''This package contains OASIS''',
    license='Apache 2.0',
    author='OSG Technology Investigation Group',
    author_email='jcaballero@bnl.gov',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='http://www.opensciencegrid.org',
    packages=['oasispackage',
              'oasispackage.distributionplugins',
              'oasispackage.probes',
              ],
    scripts = [# =============================
               #    main scripts   
               # =============================
               'bin/oasis',
               'bin/oasis-user-preinstall',
               'bin/oasis-user-publish',
               'bin/oasisd',

               # =============================
               # OASIS 1 style tools
               # =============================
               'bin/add_osg_repository',
               'bin/blank_osg_repository',
               'bin/oasis_replica_status.sh',
               'bin/oasis_status.sh',
               'bin/osg-oasis-update',
               'bin/resign_osg_whitelist',
               'bin/set_repository_property',
               'bin/unblank_osg_repository',
               'bin/generate_replicas',

               # =============================
               #  wrappers to the probes
               # =============================
               'bin/oasis-runprobe-filesize',
               'bin/oasis-runprobe-forbiddenfiles',
               'bin/oasis-runprobe-no',
               'bin/oasis-runprobe-nodelete',
               'bin/oasis-runprobe-numberfiles',
               'bin/oasis-runprobe-quota',
               'bin/oasis-runprobe-relocatable',
               'bin/oasis-runprobe-yes',
               'bin/oasis-runprobe-readable',
              ], 
    data_files = rpm_data_files
)