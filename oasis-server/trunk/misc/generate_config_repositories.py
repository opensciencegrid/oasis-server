#!/usr/bin/python

# 
# script to generate the OASIS 2 config file  repositories.conf
# with info from OIM
#

import urllib2
import libxml2
import sys
import re

#download vosummary (for oasis enabled)
response = urllib2.urlopen("https://myosg.grid.iu.edu/vosummary/xml?summary_attrs_showoasis=on&start_type=7daysago&start_date=11%2F27%2F2012&end_type=now&end_date=11%2F27%2F2012&all_vos=on&active_value=1&oasis=on&oasis_value=1&sort_key=name")
xml = response.read()
doc = libxml2.parseDoc(xml)

for vo in doc.xpathEval("//VO"):
        voname = vo.xpathEval("Name")[0].content
        voname = re.sub(r'[^/a-z0-9]+', '', voname.lower())
        username = "ouser."+voname
        reponame = voname.upper()
    print("[%s]" %reponame)
    print("repositoryname = oasis.opensciencegrid.org")
    print("repository_src_dir = /net/nas01/Public/%s" %voname)
    print("repository_dest_dir = oasis.opensciencegrid.org")
    print("repository_src_owner = %s" %username)
    print("repository_dest_owner = oasis")
