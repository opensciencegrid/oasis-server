#!/usr/bin/python

import urllib2
import libxml2
import sys
import re

#download vosummary (for oasis enabled)
response = urllib2.urlopen("https://myosg.grid.iu.edu/vosummary/xml?summary_attrs_showoasis=on&start_type=7daysago&start_date=11%2F27%2F2012&end_type=now&end_date=11%2F27%2F2012&all_vos=on&active_value=1&oasis=on&oasis_value=1&sort_key=name")
xml = response.read()
doc = libxml2.parseDoc(xml)

dncount = 0
#parse out the VO names
for vo in doc.xpathEval("//VO"):

        #create good unixname
        voname = vo.xpathEval("Name")[0].content
        voname = re.sub(r'[^/a-z0-9]+', '', voname.lower())

        username = "ouser."+voname
        groupname = "cvmfs"

        for manager in vo.xpathEval("OASIS/Managers/Manager"):
                #username = manager.xpathEval("Name")[0].content
                dn = manager.xpathEval("DN")[0].content
                original_dn = dn

                #sanitize dn
                dn = re.sub(r'[^/ ()=\.\-a-zA-Z0-9\':]+', '', dn)

                if original_dn != dn:
                    print >> sys.stderr, "invalid character in dn:",original_dn
                    continue

                #escape
                dn = re.sub(r'["]+', '\\\"', dn)
                
                #print voname,username,dn
                print "\""+dn+"\"",username
                dncount+=1
if dncount < 3:
    print >> sys.stderr, "dncount too small:",dncount
    sys.exit(2)

sys.exit(0)
