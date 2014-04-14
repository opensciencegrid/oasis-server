#!/bin/bash 

#
# ensures the init script is executable
#
chmod +x /etc/init.d/oasisd



#
# add the oasis daemon into chkconfig,
# so it will be started automatically when the machine is booted
#
/sbin/chkconfig --add oasisd



#
# checks that oasis.sysconfig has been placed in /etc/sysconfig/oasis.sysconfig 
#
SYSCONF=/etc/sysconfig/oasis.sysconfig
SYSCONFEXAMPLE=/etc/oasis/oasis.sysconfig-example
if [ ! -f $SYSCONF ] ; then
    cp $SYSCONFEXAMPLE $SYSCONF
fi



#
# ensures the condor_oasis_wrapper has execution permissions
#
chmod +x /usr/libexec/condor_oasis_wrapper.sh 



#
# ensures the scripts have execution permissions
#
PYTHONVERSION=`python -V 2>&1 | awk '{print $2}' | awk -F\. '{print $1"."$2}'`
SCRIPTSDIR="/usr/lib/python${PYTHONVERSION}/site-packages/oasispackage/scripts"
chmod +x ${SCRIPTSDIR}/*py



#
# creates, if not yet, directory /var/run/oasis
#
if [ ! -d /var/run/oasis/ ] ; then
    mkdir /var/run/oasis/
    chmod 766 /var/run/oasis/
fi
