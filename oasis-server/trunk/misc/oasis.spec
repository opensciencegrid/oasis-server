%define name oasis
%define version 2.0.14
%define release 1

Summary: OASIS package
Name: %{name}
Version: %{version}
Release: %{release}%{?dist} 
Source0: %{name}-%{version}.tar.gz
License: Apache 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Jose Caballero <jcaballero@bnl.gov>
###Packager: RACF <grid@rcf.rhic.bnl.gov>
###Provides: oasis
Url: http://www.opensciencegrid.org

%description
This package contains OASIS

%prep
%setup

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -pm0755 $RPM_BUILD_ROOT%{_var}/log/oasis
mkdir -pm0755 $RPM_BUILD_ROOT%{_var}/run/oasis
mkdir -pm0755 $RPM_BUILD_ROOT%{_sysconfdir}/oasis

%clean
rm -rf $RPM_BUILD_ROOT


%pre
f_create_oasis_account(){
    #
    # creates, if does not exist already, system account "oasis"
    # adding the sticky bit 
    # so everyone can write, but only each user
    # can delete her own content
    #

    id oasis &> /dev/null
    rc=$?
    if [ $rc -ne 0 ]; then
        /usr/sbin/useradd -r -m oasis --comment "OASIS account" --shell /bin/bash
        chmod 1777 /home/oasis
    fi
}
f_create_oasis_account 

%post
f_chkconfig(){
    #
    # add oasis daemon to checkconfig
    # but set it off. It is up to the sys admin to turn it on.
    # NOTE: only if operation is "install", not if it is "update"
    #

    if [ $1 -eq 1 ]; then 
        chkconfig --add oasisd
        chkconfig oasisd off
    fi
}
f_chkconfig $1


%preun
f_stop_daemon(){
    #
    # stops the daemon
    #

    if [ $1 -eq 0 ]; then
        # $1 == 0 => uninstall
        # $1 == 1 => upgrade 

        service oasisd status 1>/dev/null
        rc=$?
        if [ $rc -eq 0 ]; then
            # daemon is running...
            service oasisd stop 1>/dev/null
        fi
    fi
}

f_clean_chkconfig(){
    #
    # delete oasis daemon to checkconfig
    #

    if [ $1 -eq 0 ]; then
        # $1 == 0 => uninstall
        # $1 == 1 => upgrade 
        chkconfig --del oasisd 1>/dev/null
    fi
}
f_stop_daemon $1
f_clean_chkconfig $1

%postun
f_restart_daemon(){
    #
    # checks if the daemon is running,
    # if so, re-start it
    #

    if [ $1 -eq 1 ]; then 
        #$1 == 1 => upgrade
        #$1 == 0 => uninstall 

        service oasisd condrestart >/dev/null 2>&1
    fi
}
f_restart_daemon $1


%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc CHANGELOG LICENSE README etc/condor_oasis.conf-example

# ensure the /var/log/oasis directory has the sticky bit
# so everyone can write but each user can only delete her own content
%dir %attr(1777, root, root)  %{_var}/log/oasis

# ensure the /var/run/oasis directory has the sticky bit
# so everyone can write but each user can only delete her own content
%dir %attr(1777, root, root)  %{_var}/run/oasis

# ensure the /etc/oasis is created
%dir %attr(0755, root, root)  %{_sysconfdir}/oasis
%config(noreplace) %{_sysconfdir}/oasis/oasis.conf
%config(noreplace) %{_sysconfdir}/oasis/projects.conf
%config(noreplace) %{_sysconfdir}/oasis/repositories.conf
%config(noreplace) %{_sysconfdir}/oasis/probes.conf
%config(noreplace) %{_sysconfdir}/sysconfig/oasis
%config(noreplace) %{_sysconfdir}/logrotate.d/oasis

# ensure osg-oasis-update has execution permissions for everyone
%attr(0755, root, root) %{_bindir}/osg-oasis-update

# ensure oasis-admin-* tools has execution permissions only for root
%attr(0744, root, root) %{_sbindir}/oasis-admin-*


#-------------------------------------------------------------------------------
# Changelog
#-------------------------------------------------------------------------------
%changelog
* Sat Mar 14 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.14-1
- Change misc/generate_adduser (used on oasis-login) to also create the
  ouser directory on /net/nas01/Public

* Fri Mar 13 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.13-1
- Small changes in GOC script generate_config_projects: 
   -- only one empty <vo> probes config file
   -- more reasonable time values
   -- all repeated values into [DEFAULT] section
- Added some input options to the rsync command in plugin cvmfs21
- Update misc/generate_gridmap to the latest version that was installed on
  oasis-login
- Added misc/oasis_login_status
- Added bin/osg-oasis-batch and its worker bin/osg-batch-worker, and
  changed bin/osg-oasis-update to call it

* Wed Mar 11 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.12-1
- Small bug fixed in GOC script generate_config_projects
- Update GOC script do_oasis_update to add copying in of .cvmfsdirtab from
  network attached storage

* Mon Mar 9 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.11-1
- Prevent blank_osg_repository and and unblank_osg_repository from being
  confused by a .cvmfspublished signature that happens to start with 'S'
- Update bin/print_osg_replicas and misc/generate_replicas to accept URLs
  from OIM with a trailing slash

* Sun Mar 8 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.10-1
- Bumped to 2.0.10
- Added misc/print_oasis_vonames script to print out list of VOs
  for the oasis repository that are registered in OIM
- Added misc/oasis_status_stamp to generate /var/www/html/stamp
  on the oasis machine, and removed bin/oasis_status.sh.
- Removed bin/oasis_replica_status.sh.
- Moved bin/do_oasis_update to misc and updated it for cvmfs 2.1
- Moved bin/request_oasis_update to misc and made it work for both
  itb and production
- Updated add_osg_repository and resign_osg_whitelist for cvmfs 2.1.
- Added first version of sbin/oasis-admin-inspectrepository
  to print info from the catalogs using the python bindings

* Sat Feb 28 2015 Jose Caballero <jcaballero@bnl.gov> - 2.0.9-1
- Bumped to 2.0.9
- Added some variables to the output created by script generate_config_projects

* Wed Feb 25 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.8-1
- Bumped to 2.0.8
- Added bin/print_osg_repos to setup.py

* Tue Feb 24 2015 Jose Caballero <jcaballero@bnl.gov> - 2.0.7-1
- Bumped to 2.0.7
- added script generate_config_projects

* Thu Feb 19 2015 Jose Caballero <jcaballero@bnl.gov> - 2.0.5-2
- Bumped to 2.0.5-2
- config files, including sysconfig and logrotate, placed directly into
  final directory with final name. Only the condor config file is treated
  as doc file.
- non-needed code from config file commented out. Only minimum to allow
  the daemon to start without exploding is left.
- only one logrotate file, with no prerotate section.
  The postrotate section restart the daemon only if there is a PID file
- condor wrapper placed in /usr/libexec/oasis


* Mon Feb 16 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.5-1
- Upgraded to oasis 2.0.5 tarball which has a CHANGELOG entry of:
  * Added /usr/share/oasis/oasis_replica_status which generates
    /var/www/html/stamp file for OSG GOC monitoring

* Fri Feb 14 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.4-1
- Upgraded to oasis 2.0.4 tarball which has CHANGELOG entries of:
  * Updated blank_osg_repository for cvmfs-2.1.20
  * Moved /usr/bin/generate_replicas to /usr/share/oasis

* Thu Feb 03 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.3-1
- Upgraded to oasis 2.0.3 tarball which has CHANGELOG entries of:
  * Changed unblank_osg_repository to not print scary-looking prompt
    when cleaning up blanked repository
  * Added -a option to add_osg_repository to only and and not run snapshot
  * Fixed add_osg_repository to avoid being confused when the signature
    on .cvmfswhitelist begins with a capital N
  * Added print_osg_repos tool

* Wed Feb 02 2015 Dave Dykstra <dwd@fnal.gov> - 2.0.2-1
- Upgraded to 2.0.2-1 tarball which has CHANGELOG entries of:
  * Fixed the layout in trunk/ directory, to be equal to the one in tags
    directories.
  * Added spec file to trunk/misc directory
  * Fixed the rpm scripts to be equal to the those in the tags directories
  * Fixed the distutils files setup.py and setup.cfg
  * Fixed blank_osg_repository, unblank_osg_repository, and
    set_repository_property as detailed in OO-31
  * Changed generate_replicas to ignore blanked repositories

* Fri Nov 21 2014 Jose Caballero <jcaballero@BNL.gov> - 2.0.1-1
- Bumped to 2.0.1-1
- Added script generate_replicas

* Mon Nov 03 2014 Jose Caballero <jcaballero@BNL.gov> - 2.0.0-2
- Bumped to 2.0.0-2
- fixed bug in rpm script postun

