#!/usr/bin/python

import urllib2
import libxml2
import sys
import re

#download vosummary (for oasis enabled)
response = urllib2.urlopen("https://myosg.grid.iu.edu/vosummary/xml?summary_attrs_showoasis=on&start_type=7daysago&start_date=11%2F27%2F2012&end_type=now&end_date=11%2F27%2F2012&all_vos=on&active_value=1&oasis=on&oasis_value=1&sort_key=name")
xml = response.read()
doc = libxml2.parseDoc(xml)

#parse out the VO names
for vo in doc.xpathEval("//VO"):

        #create good unixname
        voname = vo.xpathEval("Name")[0].content
        voname = re.sub(r'[^/a-z0-9]+', '', voname.lower())

        username = "ouser."+voname

        print "id -u",username,"&>/dev/null || (/usr/sbin/useradd",username,"-G","cvmfs","-p","`/usr/bin/pwgen 24 -y -n -s` && gpasswd -a",username,"cvmfs)"
