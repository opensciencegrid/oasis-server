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

oasis_etc_files = ['etc/oasis.conf-example']
oasis_sysconfig = ['etc/oasisd.sysconfig-example']
oasis_etc_docs = ['etc/oasisprobes.conf-example', 'etc/oasisprojects.conf-example']
condor_etc_files = ['etc/condor_oasis.conf-example',]

utils_files = ['misc/generate_adduser',
               'misc/generate_condormap',
               'misc/generate_gridmap',
              ]

initd_files = ['etc/oasisd']



# -----------------------------------------------------------

rpm_data_files=[('/usr/libexec', libexec_files),
                ('/etc/oasis', oasis_etc_files),
                ('/etc/oasis', condor_etc_files),
                #('/etc/sysconfig', oasis_sysconfig),
                ('/etc/oasis', oasis_sysconfig),
                ('/usr/share/oasis', utils_files),
                #('/usr/share/doc/oasis-server-%s' %release_version, oasis_etc_docs),
                ('/etc/oasis' , oasis_etc_docs),
                ('/etc/init.d', initd_files),
               ]

# ===========================================================

# setup for distutils
setup(
    name="oasis-server",
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
              'oasispackage.probes',
              ],
    scripts = [# =============================
               #    main scripts   
               # =============================
               'bin/oasis',
               'bin/oasis_new',  # temporary script. It will replace oasis
               'bin/oasisd',
               #'bin/runprobes', #temporary script, to be merge with oasis

               # =============================
               #    admin tools 
               # =============================
               #'bin/osg-oasis-update',
               'bin/oasis-admin-addproject',
               #'bin/oasis-admin-delproject',
               #'bin/oasis-admin-list',
               #'bin/oasis-admin-rollback',
                               
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
