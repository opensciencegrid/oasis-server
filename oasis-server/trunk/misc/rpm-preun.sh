#!/bin/bash 
#


f_stop_daemon(){
    #
    # stops the daemon
    #

    service oasisd stop 1>/dev/null
}

f_clean_chkconfig(){
    #
    # delete oasis daemon to checkconfig
    # NOTE: only if operation is "uninstall"
    #

    if [ $1 -eq 0 ]; then
        chkconfig --del oasisd 2>/dev/null
    fi
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_clean_chkconfig $1


