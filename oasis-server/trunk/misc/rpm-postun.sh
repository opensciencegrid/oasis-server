#!/bin/bash 
#

f_restart_daemon(){
    #
    # checks if the daemon is running,
    # if so, re-start it
    #

    # FIXME: should it be done using service oasisd  condrestart ???

    if [ $1 -eq 1 ]; then 
        #$1 == 1 => upgrade
        #$1 == 0 => uninstall 

        service oasisd status 1>/dev/null
        rc=$?
        if [ $rc -eq 0 ]; then
            # daemon is running...
            service oasisd restart 1>/dev/null
        fi
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_restart_daemon $1
