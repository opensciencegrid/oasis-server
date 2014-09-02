%define name oasis
%define version 2.0.0
%define release 1

Summary: OASIS package
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: Apache 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Jose Caballero <jcaballero@bnl.gov>
Packager: RACF <grid@rcf.rhic.bnl.gov>
Provides: oasis
Obsoletes: oasis-server
Url: http://www.opensciencegrid.org

%description
This package contains OASIS

%prep
%setup

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%pre
#!/bin/#!/bin/bash  
#

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
        useradd -r -m oasis
        chmod 1777 /home/oasis
    fi
}



f_stop_daemon(){
    #
    # checks if the daemon is running,
    # if so, stops it
    #

    if [ $1 -eq 2 ]; then 
        #$1 == 2 => upgrade
        #$1 == 1 => install 
        # FIXME: should we check if RC == 1 (dead but PID file exists) or RC == 2 (dead but subsys locked)?
        # FIXME: how does this translate to the final spec file?

        service oasisd status 1>/dev/null
        rc=$?
        if [ $rc -eq 0 ]; then
            # daemon is running...
            service oasisd stop 1>/dev/null
        fi
    fi
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_create_oasis_account 
##f_stop_daemon $1


%post
#!/bin/#!/bin/bash  

f_wrapper_permissions(){
    #
    # ensures the condor_oasis_wrapper has execution permissions
    # NOTE: this actually maybe should be done separately, 
    #       since it is a pure CE task, more than OASIS
    #

    chmod +x /usr/libexec/condor_oasis_wrapper.sh 
}

f_user_client_permissions(){
    #
    # ensures the osg-oasis-update script has execution permissions
    #

    chmod +x /usr/bin/osg-oasis-update 
}

f_permissions(){
    #  
    # enforces certain permissions set for some CLI programs
    #

    # oasis-admin-* executable only by root
    chmod 744 /usr/bin/oasis-admin-*

}
   
f_create_log_directory(){
    #
    # creates directory /var/log/oasis/
    # adding the sticky bit 
    # so everyone can write, but only each user
    # can delete her own content
    #

    if [ ! -d /var/log/oasis ]; then
        mkdir /var/log/oasis
        chmod 1777 /var/log/oasis
    fi
}

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
        useradd -r -m oasis
        chmod 1777 /home/oasis
    fi
}

f_create_run_directory(){
    #
    # creates directory /var/run/oasis/
    # adding the sticky bit 
    # so everyone can write, but only each user
    # can delete her own content
    #

    if [ ! -d /var/run/oasis ]; then
        mkdir /var/run/oasis
        chmod 1777 /var/run/oasis
    fi
}
    
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

f_start_daemon(){
    #
    # starts the daemon
    #
    
    # FIXME
    # what about when the RPM is installed on the login host, which does not need daemon?
    
    service oasisd start 1>/dev/null
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  
# #f_wrapper_permissions
# #f_user_client_permissions
# f_permissions
# f_create_log_directory
# f_create_oasis_account
# f_create_run_directory
f_chkconfig $1
#f_start_daemon


%preun
#!/bin/#!/bin/bash  
#


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

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_stop_daemon $1
f_clean_chkconfig $1




%postun
#!/bin/#!/bin/bash  
#

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

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_restart_daemon $1


%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc CHANGELOG LICENSE README

