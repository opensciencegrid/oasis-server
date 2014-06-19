#!/bin/bash 

## maximum time since a snapshot was made (one day)
max_snap_age=86400

## warning time since the catalog was signed (15 minutes)
warn_snap_age=900

## number of squid processes that must be running
need_squids=2

## required number of httpd running
need_httpd=4

overall_status=0

## determine snapshot age
#snapdate=`ls -latr /srv/cvmfs/oasis/pub/catalogs* | awk -F- '{print $3}'`
#y=`echo $snapdate | colrm 5 100`
#m=`echo $snapdate | colrm 1 4 | colrm 3 100`
#d=`echo $snapdate | colrm 1 6 | colrm 3 100`
#h=`echo $snapdate | colrm 1 8 | colrm 3 100`
#mi=`echo $snapdate | colrm 1 10 | colrm 3 100`
#s=`echo $snapdate | colrm 1 12 | colrm 3 100`
#snapped=`date -d "$y-$m-$d $h:$mi:$s" +%s`

snapdate=`cat /srv/cvmfs/oasis.opensciencegrid.org/.cvmfs_last_snapshot`
snapped=`date -d "$snapdate" +%s`

now=`date +%s`
snap_age=`expr $now - $snapped`

if [ $snap_age -ge $max_snap_age ] ; then
## go to critical
   overall_status=2
fi
if [ $snap_age -ge $warn_snap_age ] ; then
## go to warning, can snapshot here if that is a good idea
   overall_status=1
fi

## are the squid processes running?
squids=`ps -e | grep -c squid`

squid_status="yes"
if [ $squids -lt $need_squids ] ; then
   overall_status=2
   squid_status="no"
fi

## are there httpd processes running?
httpds=`ps -e | grep -c httpd`

httpd_status="yes"
if [ $httpds -lt $need_httpd ] ; then
   overall_status=2
   httpd_status="no"
fi

if [ $overall_status -eq 0 ]; then
   echo "OK" > /var/www/html/stamp
fi
if [ $overall_status -eq 1 ]; then
   echo "WARNING" > /var/www/html/stamp
fi
if [ $overall_status -eq 2 ]; then
   echo "CRITICAL" > /var/www/html/stamp
fi

echo "last_snapshot:$snapped" >> /var/www/html/stamp
echo "snapshot_age:$snap_age" >> /var/www/html/stamp
echo "squid_running:$squid_status" >> /var/www/html/stamp
echo "httpd_running:$httpd_status" >> /var/www/html/stamp
