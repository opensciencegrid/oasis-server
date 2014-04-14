#!/bin/bash 

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
    # realizes there is new content and
    # re-publish. 
    # If after a given time it didn't happen,
    # return an error code
    #

    PYTHONVERSION=`python -V 2>&1 | awk '{print $2}' | awk -F\. '{print $1"."$2}'`
    SCRIPTPATH=/usr/lib/python${PYTHONVERSION}/site-packages/oasispackage/scripts

    echo "==== waiting for CVMFS to republish starts ===="
    python ${SCRIPTPATH}/cvmfs_republish.py
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

