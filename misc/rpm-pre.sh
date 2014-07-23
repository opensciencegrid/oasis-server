#!/bin/bash 
#

# FIXME: should we check if RC == 1 (dead but PID file exists) or RC == 2 (dead but subsys locked)?

# FIXME: how does this translate to the final spec file?

f_stop_daemon(){
    #
    # checks if the daemon is running,
    # if so, stops it
    #

    service oasisd status 1>/dev/null
    rc=$?
    if [ $rc -ne 0 ]; then
        # daemon is running...
        service oasisd stop 1>/dev/null
    fi

}


f_stop_daemon
