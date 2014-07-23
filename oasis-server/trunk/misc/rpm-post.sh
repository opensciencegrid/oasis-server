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
    #

    chkconfig --add oasisd
    chkconfig oasisd off
}

f_start_daemon(){
    #
    # starts the daemon
    #
    
    service oasisd start 1>/dev/null
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

#f_wrapper_permissions
#f_user_client_permissions
f_create_log_directory
f_create_oasis_account
f_create_run_directory
f_chkconfig
f_start_daemon
