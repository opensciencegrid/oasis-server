#!/usr/bin/env python 

"""
convert HTML (as created by text2html.py)
back into ascii
"""

import sys
import re

# lines we are looking for are like this
#   <tr><td>;afsdas asfasf asd fasfa faf</td><td><a href="http:ff">http:ff</a></td></tr>
p = re.compile(r'<tr><td>(.*)</td><td><a href="(.*)">(.*)</a></td></tr>')

src = sys.argv[1] 
f = open(src)

lines = f.readlines()
for line in lines:
    line = line.strip()
    if line in ['<html>', '<body>', '<table>', '</table>', '</body>', '</html>', '<tr><td>&nbsp;</td><td>&nbsp;</td></tr>']:
        continue
    if line == "":
        print
    else:
        m = p.match(line)
        print m.groups()[0], m.groups()[2]


