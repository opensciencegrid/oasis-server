#!/bin/bash 

#
# ensures the condor_oasis_wrapper has execution permissions
#
#chmod +x /usr/libexec/condor_oasis_wrapper.sh 

#
# ensures the osg-oasis-update script has execution permissions
#
#chmod +x /usr/bin/osg-oasis-update 


# FIXME !! temporary solution
# enforce /var/log/oasis.log is writeable
touch /var/log/oasis/oasis.log
chmod go+w /var/log/oasis/oasis.log

# FIXME !! temporary solution??
# creates, if does not exist already, system account "oasis"
id oasis &> /dev/null
rc=$?
if [ $rc -ne 0 ]; then
    useradd -r -m oasis
fi

