#!/bin/bash 
#

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
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_stop_daemon
