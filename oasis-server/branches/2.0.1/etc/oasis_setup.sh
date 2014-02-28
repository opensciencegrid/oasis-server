#!/bin/bash 

#  --------------------------------------------------------
#   setup file for OASIS 1.0.1
#  --------------------------------------------------------

VO=`voms-proxy-info -vo`

#
# OASIS_USER_WORKING_DIRECTORY is the directory where the 
# user will allocate their new content,
# and where the OASIS 1 scripts will place lock files
#

#export OASIS_USER_WORKING_DIRECTORY=/net/nas01/Public
export OASIS_USER_WORKING_DIRECTORY=/home
export OASIS_DESTINATION_DIRECTORY=/cvmfs/$VO.opensciencegrid.org/

