#!/usr/bin/env python 

'''
create .catalogdirs in root of cmvfs scratch area

maximum files per catalog =  

CVMFS is supposed to deal with new *and removed* .cvmfscatalog files during a publishing attempt. 

Catalogs should contain between 1000 and 200,000 files. 


'''
import os
import sys

from posix import *
try:
    from posix import _exit
except ImportError:
    pass
import posixpath as path


# Since script is in package "certify" we can know what to add to path
(libpath,tail) = os.path.split(sys.path[0])
#print(libpath)
nlibpath = os.path.split(libpath)[0]
print(nlibpath)
print(tail)
sys.path.append(nlibpath)

from oasispackage.interfaces import BaseProbe


def mywalk(top, topdown=True, onerror=None, followlinks=False):
    '''
     Customized version of os.walk which does a deterministic listing by sorting dirnames
     after retrieval rather than depending on inode order. 
    '''
    
    islink, join, isdir = path.islink, path.join, path.isdir

    # We may not have read permission for top, in which case we can't
    # get a list of the files the directory contains.  os.path.walk
    # always suppressed the exception then, rather than blow up for a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic is copied here.
    try:
        # Note that listdir and error are globals in this module due
        # to earlier import-*.
        names = listdir(top)
    except error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        if isdir(join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    dirs.sort()

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = join(top, name)
        if followlinks or not islink(new_path):
            for x in mywalk(new_path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs


class makecatalogdirs(BaseProbe):

    def __init__(self, options):
        super(makecatalogdirs, self).__init__(options)

    def run(self):
        print("src = %s dest = %s" % (self.rootdir, self.destdir))
        
        running_total = 0
        absolute_total = 0
        
        for root, dirs, files in mywalk(self.rootdir, topdown=False, onerror=None, followlinks=False):
            print(root)
            print(" %s" % dirs)
            print(" %d files" % len(files))


if __name__ == '__main__':
    probe = makecatalogdirs(sys.argv[1:])
    rc = probe.run() 
    sys.exit(rc)