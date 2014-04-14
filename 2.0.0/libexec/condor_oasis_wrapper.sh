#!/bin/bash 


OASISVERSION="2.0.0"

#
# ----------------------------------------------------------------------------
#
#   This is the CONDOR USER WRAPPER for OASIS.
#   The Condor configuration variable USER_JOB_WRAPPER points to this script. 
#   A file /etc/condor_oasis.conf is provided including this setup.
#
#   This script will basically run the user command, 
#   but also some other things, like some checks on the host, and
#   invoking the osg-oasis-update publishing command after user jobs end.
#
#   Author jcaballero (AT) bnl.gov
#    
# ----------------------------------------------------------------------------
#



# ------------------------------------------------------------------------- #  
#                 A U X I L I A R Y       F U N C T I O N S                 #
# ------------------------------------------------------------------------- # 


f_print_line(){
        echo "------------------------------------------------------------"
}

f_print_info_msg(){
        INFOMSG="$@"
        f_formatted_msg '[INFO] ' "$INFOMSG"
        echo "$FORMATTEDMSG" 
}

f_print_warning_msg(){
        WARNINGMSG="$@"
        f_formatted_msg '[WARNING] ' "$WARNINGMSG"
        echo "$FORMATTEDMSG" 
}

f_print_error_msg(){
        ERRORMSG="$@"
        f_formatted_msg '[ERROR] ' "$ERRORMSG"
        echo "$FORMATTEDMSG" | tee /dev/stderr
}

f_formatted_msg(){
        MSG="$@"

        T=`date -u +"%Y-%m-%d %H:%M:%S,%N"`
        T=${T:0:23}
        T=$T" (UTC) - OASIS "

        FORMATTEDMSG=$T"$MSG"
}

f_calculate_time(){
    #
    # calculates the difference between two times,
    # in a human friendly format:
    #          dd:hh:mm:ss
    #

    STARTTIME=$1
    ENDTIME=$2
    TOTALTIME=$((ENDTIME-STARTTIME))
    TOTALTIMEHUMAN=`printf "%dd:%dh:%dm:%ds" $((TOTALTIME/86400)) $((TOTALTIME%86400/3600)) $((TOTALTIME%3600/60)) $((TOTALTIME%60))`
}

# ------------------------------------------------------------------------- #  
#                 C H E C K     E N V I R O N M E N T                       #
# ------------------------------------------------------------------------- # 

f_platform_info(){
    #
    # some profile info
    #

    f_print_line
    echo "OASIS running at..."
    echo "OASIS VERSION: " $OASISVERSION
    echo "date (UTC):    " `date --utc`
    echo "hostname:      " `hostname`
    echo "working dir:   " `pwd`
    echo "user:          " `id`
    echo "               " `getent passwd \`whoami\``
    f_print_line
    f_print_info_msg "environment:"
    /bin/env | sort
    echo
    f_print_line
}


# ------------------------------------------------------------------------- #  
#                 E X E C U T I O N                                         #
# ------------------------------------------------------------------------- # 


f_source_setup(){
    # 
    # source the OASIS setup file
    #

    . /etc/oasis/oasis_setup.sh
}

f_get_vo(){
    #
    # find out the VO from the X509 file
    #
    
    VO=`voms-proxy-info -vo`
}

f_pre_run_user_job(){
    #
    # some preliminary preparations
    # before running the end user payload:
    #
    #   1. find out the VO
    #   2. setting up $OSG_APP to user home area
    #      by combining OASIS_USER_WORKING_DIRECTORY (from oasis_setup.sh)
    #      and the VO
    #
    
    f_get_vo
     
    export OSG_APP=${OASIS_USER_WORKING_DIRECTORY}/ouser.$VO  
    f_print_info_msg "environment variable OSG_APP setup to "$OSG_APP
}

f_run_user_job(){
    #
    # running the user command 
    #

    f_print_info_msg "running user job starts"

    STARTTIME=`date +%s`
    eval $@
    rc=$?
    ENDTIME=`date +%s`
    f_calculate_time $STARTTIME $ENDTIME

    f_print_info_msg "running user job ends"
    if [ "$rc" == "0" ] || [ "$rc" == "" ]; then
        f_print_info_msg "return code from the user job: $rc"
    else
        f_print_warning_msg "return code from the user job: $rc"
    fi 
    f_print_info_msg "user job has been running for $TOTALTIME seconds ($TOTALTIMEHUMAN)"
    echo

    return $rc
}

f_cvmfs_publish(){
    #
    # this version, for OASIS 2.0.0, just run 
    # the script osg_oasis_update, 
    # as it is done in OASIS 1 by interactive users
    #

    f_print_info_msg "updating CVMFS server with new content starts"

    STARTTIME=`date +%s`

    # ching script osg_oasis_update exists in the PATH
    command -v osg_oasis_update >/dev/null 2>&1
    if [ "$?" != "0" ]; then
        f_print_error_msg "osg_oasis_update is not in the PATH, exiting"
        exit 1 
    fi

    #osg-oasis-update $VO   # would that break OASIS 1 ???
    osg-oasis-update
    
    rc=$?
    ENDTIME=`date +%s`
    f_calculate_time $STARTTIME $ENDTIME

    f_print_info_msg "updating CVMFS server with new content ends"
    if [ "$rc" == "0" ] || [ "$rc" == "" ]; then
        f_print_info_msg "return code from updating CVMFS taks: $rc"
    else
        f_print_warning_msg "return code from updating CVMFS taks: $rc"
    fi 
    f_print_info_msg "updating CVMFS server task ran for $TOTALTIME seconds ($TOTALTIMEHUMAN)"
    echo
    return $rc
}

f_exit(){
    #
    # leave the wrapper.
    # Print out a message in case of early leaving because failure
    #

    if [ "$1" == "0" ] || [ "$1" == "" ]; then
        f_print_info_msg 'OASIS ends'
        exit 0
    else
        f_print_error_msg "Failure. Exiting with return code $1" 
        f_print_info_msg 'OASIS ends'
        exit $rc
    fi
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_main(){


    f_print_info_msg 'OASIS starts'

    # print out some platform info
    f_platform_info

    # source the OASIS setup
    f_source_setup

    # run some preliminary steps prior running the end user payload
    f_pre_run_user_job

    # run the end user payload
    f_run_user_job $@
    rc=$?
    if [ $rc -ne 0 ]; then
        f_exit $rc
    fi 

    # running the CVMFS publishing
    f_cvmfs_publish
    rc=$?
    f_exit $rc
}

f_main $@

