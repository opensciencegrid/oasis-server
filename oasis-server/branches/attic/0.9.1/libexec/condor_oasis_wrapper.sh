#!/bin/bash 

# ============================================================================ 
#
#   This is the CONDOR USER WRAPPER for OASIS.
#   The Condor configuration variable USER_JOB_WRAPPER points to this script. 
#
#   This script will basically run the user command, 
#   but also some other things, like some checks on the host, and
#   invoking the cvmfs re-publishing command after user jobs end.
#
# ============================================================================ 


f_init(){
    #
    # some profile info
    #

    echo "====  Profile information starts ===="
    echo "date (UTC):  " `date --utc`
    echo "hostname:    " `hostname`
    echo "working dir: " `pwd`
    echo "user:        " `id`
    getent passwd `whoami`
    echo "environment:"
    /bin/env | sort
    echo "====  Profile information ends ===="
    echo
}

f_run_user_job(){
    #
    # running the user command 
    #

    echo "==== running user job starts ===="
    eval $@
    rc=$?
    echo "==== running user job ends ===="
    echo
    return $rc
}

f_wait_until_cvmfs_republish(){
    #
    # wait until the CVMFS server daemon
    # realizes there is new content and re-publish. 
    # If after a given time it didn't happen,
    # return an error code
    #
    # Script to re-publish is placed underneath
    # <OASIS_PACKAGE_DIRECTORY>/scripts/
    # where the <OASIS_PACKAGE_DIRECTORY> is like
    # /usr/lib/python${PYTHONVERSION}/site-packages/oasispackage/
    # 
    # python -V returns something like Python 2.4.3
    # After some parsing, variable PYTHONVERSION has value 2.4
    # and, therefore, final path looks like
    #   /usr/lib/python2.4/site-packages/oasispackage/
    #

    PYTHONVERSION=`python -V 2>&1 | awk '{print $2}' | awk -F\. '{print $1"."$2}'`
    SCRIPTPATH=/usr/lib/python${PYTHONVERSION}/site-packages/oasispackage/scripts

    echo "==== waiting for CVMFS to republish starts ===="
    #python ${SCRIPTPATH}/cvmfs_republish.py
    python ${SCRIPTPATH}/cvmfs_republish_db.py
    rc=$?
    echo "==== waiting for CVMFS to republish ends ===="
    echo
    return $rc
}

f_exit(){
    #
    # leave the wrapper.
    # Print out a message in case of early leaving because failure
    #

    if [ "$1" == "0" ] || [ "$1" == "" ]; then
        echo '==== OASIS wrapper ends ===='
        exit 0
    else
        echo "Failure. Exiting with return code $1" 
        echo '==== OASIS wrapper ends ===='
        exit $rc
    fi
}

# ------------------------------------------------------------------------- #  
#                           M A I N                                         # 
# ------------------------------------------------------------------------- #  

f_main(){
    echo '==== OASIS wrapper starts ===='
    f_init
    f_run_user_job $@
    echo "return code from the user job $rc"
    if [ $rc -ne 0 ]; then
        f_exit $rc
    fi 
    f_wait_until_cvmfs_republish
    rc=$?
    f_exit $rc
}

f_main $@

