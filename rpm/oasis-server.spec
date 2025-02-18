Summary: OASIS server package
Name: oasis-server
Version: 3.14
Release: 1%{?dist} 
Source0: %{name}-%{version}.tar.gz
License: Apache 2.0
Group: Development/Libraries
BuildArch: noarch
Url: http://www.opensciencegrid.org

Obsoletes: oasis-goc
Requires: python3-lxml

%define cvmfs_version 2.12.6

%description
This package contains OASIS server software for OSG Operations

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/usr/bin $RPM_BUILD_ROOT/usr/share/oasis

(cd share;find *|cpio -pdv $RPM_BUILD_ROOT/usr/share/oasis)
(cd bin;find *|cpio -pdv $RPM_BUILD_ROOT/usr/bin)
find etc|cpio -pdv $RPM_BUILD_ROOT
find var|cpio -pdv $RPM_BUILD_ROOT
find usr|cpio -pdv $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT

%files
/usr/bin/*
/usr/share/oasis

%package zero
Summary: files for OASIS stratum zero
Group: Development/Libraries

Requires: oasis-server = %{version}-%{release}
Obsoletes: oasis-goc-zero

# Require specific versions of packages from osg yum repo so 
#  they can't be upgraded without being tested first on itb
Requires: cvmfs-config-osg = 2.5
Requires: cvmfs = %{cvmfs_version}
Requires: cvmfs-server = %{cvmfs_version}

%description zero
This package contains files for oasis.opensciencegrid.org

%files zero
/etc/cron.d/oasis
/etc/init.d/oasis-initclean
/etc/httpd/conf.d/oasis.conf
/etc/logrotate.d/oasis
/var/www/html/robots.txt
/usr/lib/systemd/system/oasis-initclean.service
%defattr(-,root,root)

%package replica
Summary: files for OASIS stratum one
Group: Development/Libraries

Requires: oasis-server = %{version}-%{release}
Requires: cvmfs-manage-replicas
Obsoletes: oasis-goc-replica

# Require specific versions of packages from osg yum repo so 
#  they can't be upgraded without being tested first on itb
Requires: cvmfs-config-osg = 2.5
Requires: cvmfs = %{cvmfs_version}
Requires: cvmfs-server = %{cvmfs_version}
# Using a specific release (e.g. -2.1) requires adding %{?dist} but
#  that doesn't work because this builds in the devops dist.  Would
#  have to instead add a specific osg dist name, e.g. .osg36.
Requires: frontier-squid = 11:5.9

%description replica
This package contains files for oasis-replica.opensciencegrid.org

%files replica
/etc/cron.d/cvmfs
/etc/init.d/oasis-replica-initclean
/etc/squid/oasiscustomize.sh
/etc/httpd/conf.d/cvmfs.conf
/etc/logrotate.d/cvmfs
/etc/sysconfig/frontier-squid
/var/www/html/robots.txt
/usr/lib/systemd/system/oasis-replica-initclean.service
%defattr(-,root,root)

%post
# reload apache if it is active
for service in httpd; do
    if systemctl is-active --quiet $service; then
        systemctl reload $service
    fi
done

%post replica
# redirect customize.sh to oasiscustomize.sh; we can't directly install
#  customize.sh because that's made by the frontier-squid package.
(
echo "#!/bin/bash"
echo ". /etc/squid/oasiscustomize.sh"
) >/etc/squid/customize.sh
chmod +x /etc/squid/customize.sh

# reload apache and frontier-squid if they are active
for service in httpd frontier-squid; do
    if systemctl is-active --quiet $service; then
        systemctl reload $service
    fi
done


%package login
Summary: files for OASIS login host
Group: Development/Libraries

Requires: oasis-server = %{version}-%{release}
Obsoletes: oasis-goc-login

%description login
This package contains files for oasis-login.opensciencegrid.org

%files login
/etc/logrotate.d/oasis
/etc/cron.d/oasis-login
%defattr(-,root,root)


%changelog
* Tue Feb 18 2025 John Thiltges <jthiltges@unl.edu> - 3.14-1
- Update to cvmfs and cvmfs-server 2.12.6

* Tue May 14 2024 Dave Dykstra <dwd@fnal.gov> - 3.13-1
- Update to cvmfs and cvmfs-server 2.11.3

* Fri Apr  5 2024 Dave Dykstra <dwd@fnal.gov> - 3.12-1
- Add the "-i" option cvmfs_server check -a to check the integrity of
  all files.  That makes the data chunk existense check unnecessary,
  so also add the "-c" option which greatly speeds up the checks.
- Update to cvmfs and cvmfs-server 2.11.2
- Update to frontier-squid 5.9

* Thu Jun 29 2023 Dave Dykstra <dwd@fnal.gov> - 3.11-1
- Remove the "-c" from manage-replicas in generate_replicas, so it will
  cleanup from failed adds of new repository and so avoid "initial
  snapshot in progress" warnings from monitoring.

* Thu Mar 23 2023 Dave Dykstra <dwd@fnal.gov> - 3.10-1
- Make python3 usable on both el7 & el8 by converting python tools from
  libxml2 to lxml.
- Require python3-lxml on all hosts.
- Make each of the subpackages require the main package.

* Tue Mar 21 2023 Dave Dykstra <dwd@fnal.gov> - 3.9-1
- Update cvmfs & cvmfs-server to 2.10.1, including removing the use
  of the sem command for snapshots since limiting parallelism is 
  now built in to cvmfs-server.
- Update frontier-squid to 5.7

* Tue Aug 16 2022 John Thiltges <jthiltges2@unl.edu> - 3.8-1
- Add 30-second timeout to urlopen and curl calls (SOFTWARE-5288)

* Thu Jul 28 2022 John Thiltges <jthiltges2@unl.edu> - 3.7-1
- Convert python 2 to 3 and make EL8 compatible

* Wed Apr  6 2022 Dave Dykstra <dwd@fnal.gov> - 3.6-1
- Require cvmfs 2.9.2
- Add cvmfs_server check -a on oasis-replica and oasis-replica-itb
- Only generate ssh auth keys on oasis-login, not oasis-login-itb
- Update generate_sshauthkeys to catch json decode errors and to flush
  output to the log file

* Tue Aug 17 2021 Dave Dykstra <dwd@fnal.gov> - 3.5-1
- Fix typo in the du cron that caused it to still run on Saturday night

* Wed Aug  4 2021 Dave Dykstra <dwd@fnal.gov> - 3.4-1
- Change gc and du crons to skip Saturday night/Sunday morning so as not
  to interfere with monthly zfs scrub
- Update to frontier-squid 4.15

* Wed Mar 31 2021 Dave Dykstra <dwd@fnal.gov> - 3.3-1
- Update to cvmfs 2.8.1 and frontier-squid 4.13-5.2

* Fri Mar 12 2021 Dave Dykstra <dwd@fnal.gov> - 3.2-1
- Remove third version digit
- Require specific versions of cvmfs and frontier-squid packages from osg
- Eliminate warning from find during publish on stratum 0
- Make remove_osg_repository work on stratum 0 or stratum 1
- Reverse the order of copy_config_osg when running as unprivileged user
  on oasis-itb, so it copies to test config repo from user workspace
  instead of vice versa.

* Thu Mar 04 2021 Dave Dykstra <dwd@fnal.gov> - 3.1.0-1
- Remove all the code related to re-signing incoming repositories
- Remove blank_osg_repository, unblank_osg_repository, 
  replicate_whitelists, and set_repository_property commands
- Replace generate_replicas with a script that generates a
  manage_replicas config file and runs manage_replicas

* Tue Mar 02 2021 Dave Dykstra <dwd@fnal.gov> - 3.0.0-1
- Rename package to oasis-server, remove old code from git repo

* Thu Oct 08 2020 Dave Dykstra <dwd@fnal.gov> - 2.2.12-1
- Add generate_sshauthkeys to create ssh authorized key file entries
  for those who have such keys registered in topology.
- Limit parallel snapshots on stratum 1 to the number of cores

* Tue May 05 2020 Dave Dykstra <dwd@fnal.gov> - 2.2.11-1
- Add list of cms servers to make_stashservers_list.

* Wed Apr 08 2020 Dave Dykstra <dwd@fnal.gov> - 2.2.10-1
- Add share/make_stashservers_list and run it every 3 hours from the
    stratum zero cron.

* Thu Aug 29 2019 Marian Zvada <marian.zvada@cern.ch> - 2.2.9-1
- Remove references to cvmfs-snapshot in {add|remove}_osg_repository
- Add test to compare current github source with config-osg repo 
  to copy_config_osg (OO-236) 
- Add functionality to copy_config_osg that assists with submitting 
  a PR for changes to the config-osg repo on the -itb host

* Fri Jun 28 2019 Dave Dykstra <dwd@fnal.gov> - 2.2.8-1
- Update cron to run do_du daily (OO-267)
- Update cron to do snapshots 4 times per minute and to send log output
  to a separate file in /var/log/cvmfs for each repository (OO-266)

* Fri Jun 28 2019 Dave Dykstra <dwd@fnal.gov> - 2.2.7-1
- Add do_du script (OO-267)

* Wed Dec 12 2018 Marian Zvada <marian.zvada@cern.ch> - 2.2.6-1
- Make oasis-replica ignore If-Modified-Since requests (OO-253)

* Tue Jul 03 2018 Marian Zvada <marian.zvada@cern.ch> - 2.2.5-1
- Deny .cvmfs_master_replica on the primary service (OO-222)
- Rationalize the my.opensciencegrid.org URLs (OO-223)

* Thu Jun 21 2018 Dave Dykstra <dwd@fnal.gov> - 2.2.4-1
- Add continue option to add_osg_repository
- Add support for directory of pub keys to add_osg_repository

* Wed Jun 20 2018 Dave Dykstra <dwd@fnal.gov> - 2.2.3-1
- Finish support for UNL oasis-replica

* Wed May 02 2018 Dave Dykstra <dwd@fnal.gov> - 2.2.2-1
- Make itb checks consistent
- Don't replicate cern.ch whitelists because they are not signed by 
  OSG; they are grandfathered.

* Thu Apr 19 2018 Dave Dykstra <dwd@fnal.gov> - 2.2.1-1
- Make many changes for running at UNL.

* Mon Dec 18 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.30-1
- Change add_osg_repository to use cvmfs_server add-replica -p to avoid
  creating any apache configuration, instead of removing it after the
  fact. This is now crucial because without -p an extra wsgi configuration
  file is created which clashes with the wsgi config in cvmfs.conf.

* Mon Nov 20 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.29-1
- Remove temporary WSGI config for cvmfs-servermon because that is now
  built in to new version of cvmfs-servermon.
- Add 61 second expiration of .json on stratum 0, to be consistent with
  stratum 1.
- Add additional listening port 8080 for squid, and move apache's port
  for stratum 1s to 8880.
- Reload iptables during postinstall on oasis and oasis-replica.
- Reload httpd during postinstall on oasis as it had been on oasis-replica.
- Run cvmfs_server masterkeycard -k twice if necessary in oasis_status_stamp,
  resign_osg_whitelist, and recover_oasis_rollback, because sometimes the
  key card access fails.
- Add oasis-replica-initclean and corresponding systemd service to clean up
  reflogs at boot time, in case of rollback.
* Fri Oct 20 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.28-1
- Update cvmfs.conf to go with cvmfs-2.4.2 on oasis-replica.  Reload apache
  there if it is active, and frontier-squid too while we're at it.
* Fri Aug 11 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.27-1
- Send oasis-login cron output to log files
- Have copy_config_osg allow either itb or production key on oasis-itb's
  config repository
- Have blank_osg_repository always assume production masterkey even on itb
- Add a log message in generate_whitelists when the url changes
* Fri Aug 11 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.26-1
- Move oasis-login cron to rpm from install script
* Fri Aug 11 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.25-1
- Fix copy/paste error in etc/cron.d/oasis
* Thu Aug 10 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.24-1
- Switch to using cvmfs_server resign instead of resign_osg_whitelist
  in recover_oasis_rollback.  It requires repositories to be healthy,
  so recover_oasis_rollback first does a couple of transaction/aborts
  to clean things up.
* Thu Aug 10 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.23-1
- Try resign_osg_whitelist again if it fails during recover_oasis_rollback.
* Wed Aug 09 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.22-1
- Change resign_osg_whitelist to continue trying all repos even if one
  fails.  I have seen about a 0.1% failure rate with masterkeycard signing.
- Remove reflog files in recover_oasis_rollback
- Remove /etc/sysconfig/gsisshd from oasis-login.
* Tue Aug 08 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.21-1
- Change add_osg_repository to always add the OSG pub key, even on ITB
* Tue Aug 08 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.20-1
- Add support for masterkeycard in add_osg_repository and oasis_status_stamp
- Change resign_osg_whitelist to use new cvmfs-server-2.4.0 resign -w
  option, and work with or without masterkeycard
- Remove obsolete overlayfs override in blank_osg_repository
- Change recover_oasis_rollback to be based on new resign -p command
  along with resign_osg_whitelist
- Remove gc-all-collectable, and instead call new cvmfs_server gc -af
  from cron on oasis-replica
- Add new generate_whitelists python script for automating adding new
  repositories on the stratum 0 based on what is in OIM (as
  generate_replicas currently does on the stratum 1), and add it to
  the cron on oasis
- Reduce the oasis-replica snapshot interval from 15 minutes to 5 minutes
- Update the apache config files on oasis & oasis-replica to current
  best practice, including 61 second expiration on .cvmfs* files, and
  include the /oasissrv/cvmfs/*/.cvmfswhitelist files in the settings.

* Fri Jan 13 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.19-1
- Add oasis-initclean systemd service in oasis-goc-zero, to make sure it
  runs late enough at boot time.
- Add CVMFS_DONT_CHECK_OVERLAYFS_VERSION=true to blank_osg_repository
  to make overlayfs work with cvmfs-server-2.3.2.

* Thu Jan 12 2017 Dave Dykstra <dwd@fnal.gov> - 2.1.18-1
- Change the wget commands in add_osg_repository and update_oasis_vos
  to have --timeout=10 --tries=2 so they won't hang indefinitely if
  an external repository server is down.

* Thu Dec 29 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.17-1
- Change add_osg_repository to remove .cvmfsreflog when re-using old data.

* Wed Dec 28 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.16-1
- Add new script recover_oasis_rollback, to run after rolling back to
  a previously installed oasis or oasis-itb VM.

* Wed Dec 28 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.15-1
- Change resign_osg_whitelist to support el7.  The openssl sha1 command
  had an extra "(stdin)= " in the output on el7.  resign_osg_whitelist
  was originally based on cvmfs_server's create_whitelist() function
  which is now using "cvmfs_swissknife hash" and allowing for more
  than one hash algorithm, so now resign_osg_whitelist does as well.

* Tue Dec 27 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.14-1
- Add a '+' before the 'FollowSymLinks' option in the apache config files,
  because apache 2.4 in el7 requires that if there are any "-" options
  then any options being added have to have "+".  All of the current
  option settings chosen are default for httpd versions 2.3.11 and later,
  but leave them for now in case somebody tries running with an earlier
  version.
- Re-enable garbage collection cron.

* Tue Dec 27 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.13-2
- Replace %files /usr/bin with /usr/bin/* because el7 yum install complained
  about a conflict with another package.

* Mon Dec 05 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.13-1
- Instead of changing the cron to add a key only on oasis-replica-itb,
  change add_osg_repository to add the key on both oasis-replica-itb and
  oasis-replica.  That's because doing garbage collection on non-OSG
  repositories on oasis-replica would have the same problem that was
  seen on on OSG repositories on oasis-replica-itb; in both cases the
  the .cvmfswhitelist is replaced by one signed with a different key
  than the original.
- Comment out garbage collection in cron for now (see OO-160 for an
  explanation why).  Also for future reference set the commented hour
  to 5am instead of 1am, because the clocks at the GOC are on UTC
  time.
- Change update_oasis_vos to make sure it only runs on oasis-itb, and
  to download from oasis any changed fingerprint in each external
  repo's .cvmfswhitelist.

* Fri Dec 02 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.12-1
- Change the oasis-replica cron so that on oasis-replica-itb it will
  add the extra oasis-itb key to newly added repositories.  This is
  needed for garbage collection to work on new repositories, because
  we replace each .cvmfswhitelist file with one signed by oasis-itb.

* Fri Dec 02 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.11-1
- Add gc-all-collectable and call it from cron on oasis-replica.

* Thu Dec 01 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.10-2
- Make /etc/squid/customize.sh executable after creating it.

* Thu Dec 01 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.10-1
- Move /etc/sysconfig/frontier-squid and /etc/squid/customize.sh into
  oasis-goc-replica.  Add a %post step to redirect customize.sh into a
  separate file oasiscustomize.sh, because the former is owned by the
  frontier-squid package and would cause an rpm install conflict if we
  included it directly in this rpm.

* Wed May 18 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.9-1
- Move /etc/cron.d/cvmfs into oasis-goc-replica and /etc/cron.d/oasis into
  oasis-goc-zero.

* Wed May 18 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.8-1
- Add copy_config_osg command (OO-142)
- Change /etc/init.d/oasis-initclean to use cvmfs_server mount -a (OO-144)
- Use cvmfs-server's own cvmfs_rsync in do_oasis_update (OO-143)

* Sun Apr 10 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.7-1
- Change update_oasis_vos to not copy from nas01 (OO-136)

* Sun Mar  6 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.6-1
- Remove oasis-replica-initclean (OO-126)
- Mount all cvmfs repositories at boot in oasis-initclean (OO-126)
- Remove harmless code in update_oasis_vos that printed an error (OO-120)

* Thu Mar  3 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.5-1
- Remove dependency on nas01 (OO-120)

* Wed Mar  2 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.4-1
- Automatically add missing external repositories to oasis-itb (OO-124)
- Prevent warning when a repo hasn't finished initial snapshot (OO-115)
- Eliminate a file in communication between oasis and oasis-login (OO-116)
- Remove /etc/cvmfs/cvmfs_server_hooks.sh on oasis-replica.  It's not
    needed anymore with cvmfs-server-2.2.X (OO-126).

* Wed Mar  2 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.3-1
- Add support for cvmfs-servermon rpm (OO-125)

* Wed Feb 24 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.2-1
- Rebuild.  2.1.1 did not have the full correct set of source files
  because all the branches weren't merged together.
- Fix permission of whitelist created; mktemp made it mode 600.

* Wed Feb 24 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.1-1
- Include a bunch of minor changes.  For details see tickets OO-122, 
  OO-111, OO-109, OO-108, and OO-107.

* Fri Feb 19 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.0-1
- Extracted goc-specific pieces out of oasis package
