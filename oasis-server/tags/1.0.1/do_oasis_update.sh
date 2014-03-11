#!/bin/bash
LOCKPFX="/net/nas01/Public/"
if [ "`uname -n|cut -d. -f1`" != oasis ]; then
    LOCKPFX=${LOCKPFX}itb_
fi
## was an update requested?
if [ -f ${LOCKPFX}oasis_update_lock ]; then
## update was requested
## is an update in progress?
    if [ -f ${LOCKPFX}oasis_update_in_progress ]; then
        PID="`cat ${LOCKPFX}oasis_update_in_progress`"
        if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
            # process still running, silently exit
            exit
        fi
        now=`date`
        echo "$now overriding oasis_update_in_progress lock, pid $PID not running"
    fi
    echo $$ >${LOCKPFX}oasis_update_in_progress
    if [ -f ${LOCKPFX}vo_update_requested ]; then
##      updating a single VO
        vo=`cat ${LOCKPFX}vo_update_requested`
        now=`date`
        echo "$now starting vo update for $vo"
        su cvmfs -c "rsync -aW --stats --exclude .cvmfscatalog --exclude /.oasisdirtab --exclude /.oasisdirexclude --delete --force /net/nas01/Public/ouser.$vo/ /cvmfs/oasis.opensciencegrid.org/$vo"
    fi
    now=`date`
    echo "$now sync files from /usr/local/oasis/distrib"
    su cvmfs -c "rsync -av /usr/local/oasis/distrib/ /cvmfs/oasis.opensciencegrid.org/"
    now=`date`
    echo "$now starting expand_oasis_dirtab"
    su cvmfs -c /usr/local/oasis/bin/expand_oasis_dirtab
    stat=$?
    now=`date`
    if [ $stat -eq 0 ]; then
        echo "$now finished expand_oasis_dirtab"
    else
        echo "$now expand_oasis_dirtab returned $stat"
        echo "$now failed expand_oasis_dirtab">>/var/log/oasis/oasis_update.log
    fi
    echo "$now starting cvmfs_server publish"
    # increase the maximum number of open files because cvmfs_server
    #   keeps all catalogs it is working with open simultaneously
    ulimit -n 32768
    /usr/bin/cvmfs_server publish
    stat=$?
    now=`date`
    if [ $stat -eq 0 ]; then
        echo "$now finished cvmfs_server publish"
    else
        echo "$now cvmfs-server publish returned $stat"
        echo "$now finished cvmfs_server publish">>/var/log/oasis/oasis_update.log
    fi
    rm -f ${LOCKPFX}oasis_update_in_progress
    rm -f ${LOCKPFX}oasis_update_lock
    /usr/local/oasis/bin/oasis_status.sh
fi >>/var/log/oasis_update.log 2>&1
exit 0

