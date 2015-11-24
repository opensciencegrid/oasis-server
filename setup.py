#!/usr/bin/env python
#
# Setup prog for OASIS 
#
#
release_version='2.0.38'

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

utils_files = ['misc/cvmfs_server_hooks.sh',
               'misc/cvmfs_rsync',
               'misc/do_oasis_update',
               'misc/generate_adduser',
               'misc/generate_condormap',
               'misc/generate_gridmap',
               'misc/generate_replicas',
               'misc/generate_config_projects',
    	       'misc/oasis-batch-worker',
    	       'misc/oasis_login_status',
    	       'misc/oasis_replica_status',
    	       'misc/oasis_status_stamp',
               'misc/print_oasis_vonames',
    	       'misc/replicate_whitelists',
    	       'misc/request_oasis_update',
    	       'misc/update_oasis_vos',
              ]

initd_files = ['etc/oasisd',
	       'etc/oasis-initclean',
	       'etc/oasis-login-initclean',
	       'etc/oasis-replica-initclean',
	      ]

etc_files = ['etc/oasis.conf',
             'etc/projects.conf',
             'etc/repositories.conf',
             'etc/probes.conf',
            ]

sysconfig_files = ['etc/sysconfig/oasis',
                  ]

logrotate_files = ['etc/logrotate/oasis']

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

rpm_data_files=[('/usr/libexec/oasis', libexec_files),
                ('/usr/share/oasis', utils_files),
                ('/etc/init.d', initd_files),
                ('/etc/oasis', etc_files),
                ('/etc/sysconfig', sysconfig_files),
                ('/etc/logrotate.d', logrotate_files),
                ('/usr/sbin', sbin_files),

                # custom GOC-only config files, 
                # to be added to 3 extra RPMs, 
                # as a temporary solution 
                # before they are managed by puppet
                ('/etc/cron.d', ['etc/configs/oasis/cron_oasis']),
                ('/etc/httpd/conf.d', ['etc/configs/oasis/httpd_cvmfs.conf']),
                ('/etc/iptables.d', ['etc/configs/oasis/60-local-iptables-oasis']),
                ('/var/www/html', ['etc/configs/oasis/robots.txt']),
            
                ('/etc/iptables.d', ['etc/configs/oasis-replica/60-local-iptables-cvmfs']),
                ('/etc/httpd/conf.d', ['etc/configs/oasis-replica/httpd_cvmfs.conf']),
                ('/etc/logrotate.d', ['etc/configs/oasis-replica/logrotate_cvmfs']),
                ('/var/www/html', ['etc/configs/oasis-replica/robots.txt']),
                ('/etc/squid', ['etc/configs/oasis-replica/squid_customize.sh']),

                ('/etc/iptables.d', ['etc/configs/oasis-login/60-local-iptables-oasis-login']),
                ('/etc/sysconfig', ['etc/configs/oasis-login/gsisshd']),

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
              'oasispackage.plugins',
              'oasispackage.plugins.distribution',
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
               'bin/osg-batch-update',
               'bin/osg-oasis-update',
               'bin/print_osg_repos',
               'bin/resign_osg_whitelist',
               'bin/set_repository_property',
               'bin/unblank_osg_repository',

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
