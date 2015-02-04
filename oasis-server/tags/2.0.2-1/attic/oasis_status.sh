#!/bin/bash

## maximum time since a publish (25 days)
threshold=2160000

## maximum time since the catlog was signed (30 days)
max_sig_age=2592000

## warning time since the catalog was signed (25 days)
warn_sig_age=2160000

overall_status=0

## create a file summarizing oasis status

update_time=`ls -la --time-style +%s /srv/cvmfs/oasis.opensciencegrid.org/pub/catalogs/.*.x509 | awk '{print $6}'`
now=`date +%s`

page=`expr $now - $update_time`

## was the last update within the allowed age?
if [ $page -ge $threshold ] ; then
   overall_status=2
## can do a re-publish here if this turns out to be a good idea
fi

## check that various processes exist
condor=`ps -e | grep condor_master | awk '{print $4}'`

if [ $condor ]; then
   cstat="yes"
else
   cstat="no"
   overall_status=2
fi

/sbin/service cvmfsd status 1>/dev/null 2>/dev/null
status=$?
if [ $status -eq 0 ]; then
   ostat="yes"
else
   if [ -f /net/nas01/Public/oasis_update_in_progress ]; then
       ostat="Update_in_progress"
       overall_status=1
   else
       ostat="no"
       overall_status=2
   fi
fi


## calculate how long ago the catalog was signed
## date is in strange format, parse it
signdate=`head -n 1 /srv/cvmfs/oasis.opensciencegrid.org/pub/catalogs/.cvmfswhitelist`
y=`echo $signdate | colrm 5 100`
m=`echo $signdate | colrm 1 4 | colrm 3 100`
d=`echo $signdate | colrm 1 6 | colrm 3 100`
h=`echo $signdate | colrm 1 8 | colrm 3 100`
mi=`echo $signdate | colrm 1 10 | colrm 3 100`
s=`echo $signdate | colrm 1 12 | colrm 3 100`

signed=`date -d "$y-$m-$d $h:$mi:$s" +%s`
now=`date +%s`
age=`expr $now - $signed`

if [ $age -ge $max_sig_age ] ; then
## go to critical
   overall_status=2
fi
if [ $age -ge $warn_sig_age ] ; then
## go to warning, can re-sign here if that is a good idea
   overall_status=1
fi

age=`expr $age / 86400`

if [ $overall_status -eq 0 ]; then
   echo "OK" > /var/www/html/stamp
fi
if [ $overall_status -eq 1 ]; then
   echo "WARNING" > /var/www/html/stamp
fi
if [ $overall_status -eq 2 ]; then
   echo "CRITICAL" > /var/www/html/stamp
fi

echo "last_published:$update_time" >>/var/www/html/stamp
echo "publish_age:$page" >> /var/www/html/stamp
echo "signature_age_days:$age" >> /var/www/html/stamp
echo "condor_running:$cstat" >> /var/www/html/stamp
echo "cvmfsd_running:$ostat" >> /var/www/html/stamp

## cat /var/www/html/stamp

