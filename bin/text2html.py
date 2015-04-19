#!/usr/bin/env python 

"""
convert ascii text into HTML. 
Source is like this:

    af adfa adfaf  http://foo
    fa gad falf ad f  h http://bar
"""

import sys

src = sys.argv[1] 
f = open(src)

blocks = []
class Block:
    def __init__(self):
        self.lines = []

    def add(self, line):
        self.lines.append(line)

    def display(self):

        str = ""
        for line in self.lines:
            if line.strip() == "":
                str += '<tr><td>&nbsp;</td><td>&nbsp;</td></tr>\n'
            else:
                msg = ' '.join(line.split()[:-1])
                link = line.split()[-1]
                str += '<tr><td>'
                str += msg
                str += '</td>'
                str += '<td>'
                str += '<a href="%s">%s</a>' %(link, link)
                str += '</td></tr>\n'
        return str


block = Block()

lines = f.readlines()
for line in lines:
    if line.strip() == "":
        block.add(line)
        blocks.append(block)
        block = Block()
    else:
        block.add(line)
blocks.append(block)

# -------------------------    

print '<html>'
print '<body>'
print '<table>' 

for block in blocks:
    print block.display()

print '</table>' 
print '</body>'
print '</html>'
