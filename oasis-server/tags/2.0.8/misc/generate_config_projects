#!/usr/bin/python

# 
# script to generate the OASIS 2 config file  projects.conf
# with info from OIM
#


import commands
import libxml2
import re
import sys
import urllib2

#download vosummary (for oasis enabled)
response = urllib2.urlopen("https://myosg.grid.iu.edu/vosummary/xml?summary_attrs_showoasis=on&start_type=7daysago&start_date=11%2F27%2F2012&end_type=now&end_date=11%2F27%2F2012&all_vos=on&active_value=1&oasis=on&oasis_value=1&sort_key=name")
xml = response.read()
doc = libxml2.parseDoc(xml)

for vo in doc.xpathEval("//VO"):
    voname = vo.xpathEval("Name")[0].content
    voname = re.sub(r'[^/a-z0-9]+', '', voname.lower())
    username = "ouser."+voname
    reponame = voname.upper()
    projectname = voname
    section = projectname.upper()
    print("[%s]" %section)
    print("repositorysection = OASIS")  # For GOC, at the time being, only one repository
    print("projectname = %s" %projectname)
    print("project_src_dir = %s" %projectname )
    print("project_dest_dir = %s" %projectname)
    print("project_src_owner = %s" %username)
    print("project_dest_owner = oasis")
    print("projectprobesconf = /etc/oasis/%s.conf" %projectname)

    # FIXME. Just a temporary solution
    commands.getoutput('touch /etc/oasis/%s.conf' %projectname)

