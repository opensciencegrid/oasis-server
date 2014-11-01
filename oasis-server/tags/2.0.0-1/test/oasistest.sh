#!/bin/bash 

cd $OSG_APP/mis

FILENAME=test.`date +%F.%m.%d:%H:%M:%S`
echo "this is a testing job for OASIS" >> $FILENAME
