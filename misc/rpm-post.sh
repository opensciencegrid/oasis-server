#!/bin/bash 

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
 f_create_log_directory
# f_create_oasis_account
 f_create_run_directory
f_chkconfig $1
#f_start_daemon
