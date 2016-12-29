Summary: OASIS GOC package
Name: oasis-goc
Version: 2.1.17
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
/etc/sysconfig/gsisshd
%defattr(-,root,root)


%changelog
* Thu Dec 28 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.17-1
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

* Thu Dec 02 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.12-1
- Change the oasis-replica cron so that on oasis-replica-itb it will
  add the extra oasis-itb key to newly added repositories.  This is
  needed for garbage collection to work on new repositories, because
  we replace each .cvmfswhitelist file with one signed by oasis-itb.

* Thu Dec 02 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.11-1
- Add gc-all-collectable and call it from cron on oasis-replica.

* Wed Dec 01 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.10-2
- Make /etc/squid/customize.sh executable after creating it.

* Wed Dec 01 2016 Dave Dykstra <dwd@fnal.gov> - 2.1.10-1
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
