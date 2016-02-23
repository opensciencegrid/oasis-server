#!/bin/sh

publish_after_hook() {
    local repo_name="$1"
    echo -n "Cleaning out spooler temp dir... "
    . /etc/cvmfs/repositories.d/${repo_name}/server.conf
    [ ! -z ${CVMFS_SPOOL_DIR} ]     || { echo "fail"; exit 1; }
    rm -fR ${CVMFS_SPOOL_DIR}/tmp/* || { echo "fail"; exit 1; }
    echo "done"
} 
