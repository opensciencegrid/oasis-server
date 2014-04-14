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
	voname = vo.xpathEval("Name")[0].content

	for manager in vo.xpathEval("OASIS/Managers/Manager"):
		username = manager.xpathEval("Name")[0].content
		dn = manager.xpathEval("DN")[0].content

		#sanitize dn
		dn = re.sub(r'[^/ -=a-zA-Z0-9\':]+', '', dn)

		#escape dn
		dn = re.sub(r'["]+', '\\\"', dn) #TODO does this work?
		dn = re.sub(r'[=]+', '\\=', dn)
		dn = re.sub(r'[-]+', '\\-', dn)
		dn = re.sub(r'[/]+', '\\/', dn)
		dn = re.sub(r'[ ]+', '\\ ', dn)

		#create good unixname
		voname = re.sub(r'[^/a-z0-9]+', '', voname.lower())
		
		#print voname,username,dn
		print "GSI \"^"+dn+"\"",voname+".ouser@oasis.grid.iu.edu"

print "GSI (.*) GSS_ASSIST_GRIDMAP"
print "GSI (.*) anonymous"
print "FS (.*) \\1"
