#!/bin/bash  

# Actions done by this post-install script
#   -- create /etc/cvmfs/default.local file if it does not exist yet. 
#   -- if exists, backup the existing /etc/cvmfs/default.local file
#   -- edit it to add new CVMFS_REPOSITORIES


f_check_defaultlocal_exists(){
    # checks if file /etc/cvmfs/default.local already exists or not
    
    FILE=/etc/cvmfs/default.local
    if [ -f $FILE ] ; then 
        return 0
    else
        return 1
    fi 
}

f_create_defaultlocal(){
    # in case there is no default.local file created yet,
    # we use the candidate version distributed within the oasis-client RPM

    CANDIDATEFILE=/etc/cvmfs/default.local.candidate
    FILE=/etc/cvmfs/default.local
    cp $CANDIDATEFILE $FILE 
}

f_backup_defaultlocal(){
    # in case there is already a default.local,
    # we create a backup copy before adding new stuffs

    OLDFILE=/etc/cvmfs/default.local
    BAKFILE=/etc/cvmfs/default.local.bak
    cp $OLDFILE $BAKFILE
}

f_add_repo_to_defaultlocal(){
    # add the oasis repo to the CVMFS_REPOSITORIES field
    
    # NOTE: seems like with the new configuration,
    #       this step is not needed, 
    #       and domains are detected automagically

    TMPFILE=/etc/cvmfs/default.local.tmp
    OASISREPO="oasis.opensciencegrid.org"
    
    cat $FILE | awk -v OASISREPO=${OASISREPO} '{
        if ($0 ~ "^CVMFS_REPOSITORIES") 
            {print $0","OASISREPO} 
        else 
            {print $0}
        }' > $TMPFILE
    mv $TMPFILE $FILE
 
}

f_restart_cvmfsd(){
    # re-start the cvmfs client daemon

    /etc/init.d/cvmfs start
}

#################################################
#               M A I N                         #
#################################################

f_check_defaultlocal_exists
rc=$?
if [ $rc -eq 0 ]; then
    f_backup_defaultlocal
else
    f_create_defaultlocal
fi

# f_add_repo_to_defaultlocal

f_restart_cvmfsd
