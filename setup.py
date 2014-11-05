#!/usr/bin/env python
#
# Setup prog for OASIS 
#
#

release_version='2.0.0'

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

oasis_etc_docs = ['etc/oasis.conf-example', 'etc/probes.conf-example', 'etc/projects.conf-example', 'etc/repositories.conf-example']
oasis_sysconfig = ['etc/oasis.sysconfig-example']
oasis_logrotate = ['etc/logrotate/oasis.logrotate-example']
condor_etc_files = ['etc/condor_oasis.conf-example',]

utils_files = ['misc/generate_adduser',
               'misc/generate_condormap',
               'misc/generate_gridmap',
              ]

initd_files = ['etc/oasisd']


# -----------------------------------------------------------

rpm_data_files=[('/usr/libexec', libexec_files),
                ('/etc/oasis' , oasis_etc_docs),
                ('/etc/oasis', condor_etc_files),
                ('/etc/oasis', oasis_sysconfig),
                ('/etc/oasis', oasis_logrotate),
                ('/usr/share/oasis', utils_files),
                ('/etc/init.d', initd_files),
                #('/usr/share/doc/oasis-2.0.0', condor_etc_files),
                #('/etc/sysconfig', oasis_sysconfig),
                #('/usr/share/doc/oasis-server-%s' %release_version, oasis_etc_docs),
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
               #'bin/runprobes', #temporary script, to be merge with oasis

               # =============================
               # OASIS 1 tools
               # =============================
               'bin/add_osg_repository',
               'bin/blank_osg_repository',
               'bin/oasis_replica_status.sh',
               'bin/oasis_status.sh',
               'bin/osg-oasis-update',
               'bin/resign_osg_whitelist',
               'bin/set_repository_property',
               'bin/unblank_osg_repository',

               #'bin/do_oasis_update',
               #'bin/expand_oasis_dirtab',
               #'bin/generate_adduser',
               #'bin/generate_gridmap',
               #'bin/request_oasis_update',
               #'bin/stratumones.pl',

               # =============================
               #    admin tools 
               # =============================
               'bin/oasis-admin-projectadd',
               #'bin/oasis-admin-projectdel',
               #'bin/oasis-admin-list',
               #'bin/oasis-admin-rollback',
               'bin/oasis-admin-start',
               'bin/oasis-admin-restart',
               'bin/oasis-admin-stop',
               'bin/oasis-admin-status',
                               
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
