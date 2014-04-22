#!/usr/bin/env python 
'''
create .catalogdirs in root of cmvfs scratch area
CVMFS is supposed to deal with new *and removed* .cvmfscatalog files during a publishing attempt. 
Catalogs should contain between 1000 and 200,000 files. 

Need to do depth-first, *postorder* traversal of tree. This process needs to be *deterministic*
so that it can be done iteratively and be stable. 


for node in root:
    process all children
    process root

CORNER CASES
A: When a large number of subdirs have total files just under the threshold, 
but all taken together add up to a large number. 
  Option 1: Lower global threshold by some fraction, and re-calculate from the bottom. Do
             this until constraints are met.   
  Option 2: Implement an algorithm that can descend as well as climb a tree, such that
             it could iteratively deal with that dir without changing the global threshold. 
  Option 3: Keep track of subdirectory total files and then sort by size. Add catalogs, in 
            order, to these subdirectories until leftover is less than max. !!

B: When a directory has a very large number of files in it. 
     Should be rare, since problems arise with dirs with more than 32k files.
     
C: ?     


[makecatalogdirtab]
enabled = True
probe = yes
options = "--maxfiles 5000 "
level = warning
   
Author: John Hover <jhover@bnl.gov>   
    
'''
import getopt
import logging
import os
import stat
import sys
from operator import itemgetter

(libpath,tail) = os.path.split(sys.path[0])
#print(libpath)
nlibpath = os.path.split(libpath)[0]
print(nlibpath)
print(tail)
sys.path.append(nlibpath)

#from oasispackage.interfaces import BaseProbe
CATALOGDIRS=[]
CATALOGDIRTOTALS=[]
TABFILE_NAME=".cvmfsdirtab"

# maxfiles is threshold, absmax = maxfiles * ABS_MAX_FACTOR
# our goal is that no catalog can contain more than absmax files, 
# unless they all reside in one directory (which we can't help).
ABS_MAX_FACTOR=2

def addtocatalog(dirpath, numfiles):
    if dirpath not in CATALOGDIRS:
        print("Adding %s to catalogdirs. %d  files." % (dirpath,numfiles))
        CATALOGDIRS.append(dirpath)
        CATALOGDIRTOTALS.append(numfiles)    
    else:
        print("WARNING: tried to re-add directory to catalogdirs. %s" % dirpath)


def mywalk(top, maxfiles=250, dirtab=[]):
    '''
    postorder, depth-first processing (alphabetical)
    recursively determine how many files in subtree
    only counts files, not directories
    takes current catalog table as input
    
    '''
    totalfiles = 0
    subdirfiles = 0
    dirs = []
    files = []
    
    # contains tuples of (dirpath, numfiles)
    subdirinfo = []
    try:
        names = os.listdir(top)
        names.sort()
        for name in names:
            fullname = os.path.join(top, name)
            try:
                mode = os.lstat(fullname).st_mode
            except os.error:
                mode = 0
            if stat.S_ISDIR(mode):
                dirs.append(fullname)
            else:
                files.append(fullname)
        for dirpath in dirs:
            dirtotal = mywalk(dirpath, maxfiles=maxfiles, dirtab=dirtab)
            subdirinfo.append((dirpath, dirtotal))
            #print("subdir: %s total %d files." % (dirpath, dirtotal))
            totalfiles += dirtotal
            subdirfiles += dirtotal
        #print(subdirinfo)
        numfiles = len(files)        
        totalfiles = numfiles + totalfiles
        #print("%s: %s dirs, %d files, totalfiles=%d" % (top, 
        #                                                        len(dirs), 
        #                                                        len(files), 
        #                                                        numfiles))
    except OSError, e:
        #print("OSError: %s" % e)
        pass
    
    # sort dirs by number of subfiles. already sorted by alphabetical, so should be
    # stable. 
    subdirinfo = sorted(subdirinfo, key=itemgetter(1), reverse=True)
    print("subdirinfo: %s" % subdirinfo)
        
    if top in dirtab:
        print("%s: dir already in dirtab. Re-adding." %  top )

        totalfiles = 0
    elif totalfiles > maxfiles:
        # numfiles + subdirfiles > maxfiles
        # where is the max coming from? local or subdir?
        if subdirfiles > maxfiles:
            # the files from subdirectories passed the threshold
            i = 0
            while subdirfiles > maxfiles:
                (p,n) = subdirinfo[i]
                print("Adding subdir %s to catalogs..." % p)
                addtocatalog(p,n)
                subdirfiles = subdirfiles - n
                totalfiles = totalfiles - n
                i += 1    
        else:
            pass 

        if numfiles > maxfiles:
            addtocatalog(top, totalfiles)
            totalfiles = 0
       
    return totalfiles
               

#class makecatalogdirs(BaseProbe):
class makecatalogdirtab(object):

    def __init__(self, oasisproberootdir="/var", oasisprobedestdir="/var", maxfiles=5000):
        self.rootdir = oasisproberootdir
        self.destdir = oasisprobedestdir
        self.maxfiles = int(maxfiles)

    def run(self):
        print("src = %s dest = %s" % (self.rootdir, self.destdir))
        tablist = None
        try:
            dirtabfile = "%s/%s" % (self.rootdir, TABFILE_NAME)
            print("Attempting to open current dirtab: %s" %dirtabfile)
            f = open(dirtabfile)
            tablist = []
            for line in f.readlines():
                tablist.append(line.strip())
            f.close()
            print("%s opened OK. %s lines." % (dirtabfile, len(tablist)))
        except IOError:
            print("No such file. or unreadable: %s" % dirtabfile)        
        
        running_total = 0
        absolute_total = 0
        if tablist:
            mywalk(self.rootdir, self.maxfiles, dirtab=tablist  )
        else:
            mywalk(self.rootdir, self.maxfiles)
        print("Creating .cvmfsdirtab with %d entries:" % len(CATALOGDIRS))
        for i in range(len(CATALOGDIRS)):
            print("%s  %10d" % (CATALOGDIRS[i], CATALOGDIRTOTALS[i]))
        
        try:
            dirtabfile = "%s/%s" % (self.destdir, TABFILE_NAME)
            print("Attempting to open/write dirtab file: %s" %dirtabfile)
            f = open(dirtabfile, 'w')
            for d in CATALOGDIRS:
                f.write("%s\n" % d)
            f.close()
            print("%s written OK. %s lines." % (dirtabfile, len(CATALOGDIRS)))
        except IOError:
            print("File unwritable: %s" % dirtabfile)   
          
          
if __name__ == '__main__':
    argv = sys.argv[1:]
    usage = """
    usage: $0 [options]

Run probe against given  

OPTIONS:
    -h --help         Print help.
    -d --debug        Debug logging.      
    -v --verbose      Verbose logging. 
    -r --rootdir      Root of source path. 
    -t --destdir      Root of destination path.
    -x --maxfiles     Max files per catalog
     

"""
    # Handle command line options
    rootdir = "/var"
    destdir = "/var"


    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvr:t:x:", 
                                   ["help",
                                    "debug",
                                    "verbose", 
                                    "rootdir=", 
                                    "destdir=",
                                    "maxfiles=", 
                                    ])
    except getopt.GetoptError, error:
        print( str(error))
        print( usage )                          
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)                     
            sys.exit()            
        elif opt in ("-d", "--debug"):
            loglevel = logging.DEBUG
        elif opt in ("-v", "--verbose"):
            loglevel = logging.INFO
        elif opt in ("-r", "--rootdir"):
            rootdir = arg
        elif opt in ("-t", "--destdir"):
            dstdir = int(arg)
        elif opt in ("-x", "--maxfiles"):
            maxfiles = int(arg)
                    
    probe = makecatalogdirtab( oasisproberootdir=rootdir, oasisprobedestdir=destdir, maxfiles=maxfiles )
    rc = probe.run() 
    sys.exit(rc)
    
    