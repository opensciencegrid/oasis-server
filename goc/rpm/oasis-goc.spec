Summary: OASIS GOC package
Name: oasis-goc
Version: 2.1.25
Release: 1%{?dist} 
Source0: %{name}-%{version}.tar.gz
License: Apache 2.0
Group: Development/Libraries
#BuildRoot requried only on RHEL5
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: http://www.opensciencegrid.org

%description
This package contains OASIS software for the OSG Global Operations Center

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
%description zero
This package contains files for oasis.opensciencegrid.org

%files zero
/etc/cron.d/oasis
/etc/init.d/oasis-initclean
/etc/httpd/conf.d/oasis.conf
/etc/iptables.d/60-local-oasis
/etc/logrotate.d/oasis
/var/www/html/robots.txt
/usr/lib/systemd/system/oasis-initclean.service
%defattr(-,root,root)

%package replica
Summary: files for OASIS stratum one
Group: Development/Libraries
%description replica
This package contains files for oasis-replica.opensciencegrid.org

%files replica
/etc/cron.d/cvmfs
/etc/squid/oasiscustomize.sh
/etc/httpd/conf.d/cvmfs.conf
/etc/iptables.d/60-local-cvmfs
/etc/logrotate.d/cvmfs
/etc/sysconfig/frontier-squid
/var/www/html/robots.txt
%defattr(-,root,root)

%post replica
# redirect customize.sh to oasiscustomize.sh; we can't directly install
#  customize.sh because that's made by the frontier-squid package.
(
echo "#!/bin/bash"
echo ". /etc/squid/oasiscustomize.sh"
) >/etc/squid/customize.sh
chmod +x /etc/squid/customize.sh


%package login
Summary: files for OASIS login host
Group: Development/Libraries
%description login
This package contains files for oasis-login.opensciencegrid.org

%files login
/etc/iptables.d/60-local-oasis-login
%defattr(-,root,root)


%changelog
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
