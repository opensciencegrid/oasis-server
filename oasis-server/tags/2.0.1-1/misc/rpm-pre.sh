#!/bin/bash 
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
