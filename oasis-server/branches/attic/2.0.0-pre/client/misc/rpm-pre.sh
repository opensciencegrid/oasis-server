#!/bin/bash  

f_stop_cvmfsd(){
    # stop the cvmfs client daemon

    /etc/init.d/cvmfs stop
}

#################################################
#               M A I N                         #
#################################################

f_stop_cvmfsd

