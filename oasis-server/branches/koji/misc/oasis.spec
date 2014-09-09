%define name oasis
%define version 2.0.0
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
        /usr/sbin/useradd -r -m oasis --comment "OASIS account" --shell /bin/bash oasis
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
}
f_restart_daemon $1


%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc CHANGELOG LICENSE README

# ensure the /var/log/oasis directory has the sticky bit
# so everyone can write but each user can only delete her own content
%dir %attr(1777, root, root)  %{_var}/log/oasis

# ensure the /var/run/oasis directory has the sticky bit
# so everyone can write but each user can only delete her own content
%dir %attr(1777, root, root)  %{_var}/run/oasis

%config(noreplace) %{_sysconfdir}/oasis/oasis.conf
%config(noreplace) %{_sysconfdir}/oasis/oasisprojects.conf
%config(noreplace) %{_sysconfdir}/oasis/oasisprobes.conf
%config(noreplace) %{_sysconfdir}/sysconfig/oasisd

# ensure osg-oasis-update has execution permissions for everyone
%attr(0755, root, root) %{_bindir}/osg-oasis-update

# ensure oasis-admin-* tools has execution permissions only for root
%attr(0744, root, root) %{_sbindir}/oasis-admin-*
