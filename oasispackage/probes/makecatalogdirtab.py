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

Interesting issue: when a large number of subdirs have total files just under the threshold, 
but all taken together add up to a large number. 
  Option 1: Lower global threshold by some fraction, and re-calculate from the bottom. Do
             this until constraints are met.   
  Option 2: Implement an algorithm that can descend as well as climb a tree, such that
             it could iteratively deal with that dir without changing the global threshold. 
  Option 3: Keep track of subdirectory total files and then sort by size. Add catalogs, in 
            order, to these subdirectories until leftover is less than max. !!



[makecatalogdirtab]
enabled = True
probe = yes
options = "--maxfiles 5000 "
level = warning
    
'''
import getopt
import os
import stat
import sys

(libpath,tail) = os.path.split(sys.path[0])
#print(libpath)
nlibpath = os.path.split(libpath)[0]
print(nlibpath)
print(tail)
sys.path.append(nlibpath)

#from oasispackage.interfaces import BaseProbe
CATALOGDIRS=[]
TABFILE_NAME=".cvmfsdirtab"

def mywalk(top, maxfiles=250, dirtab=[]):
    '''
    postorder, depth-first processing (alphabetical)
    recursively determine how many files in subtree
    only counts files, not directories
    takes current catalog table as input
    
    '''
    numfiles = 0
    dirs = []
    files = []
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
            #print("subdir: %s total %d files." % (dirpath, dirtotal))
            numfiles += dirtotal
        
        numfiles = len(files) + numfiles
        #print("%s: %s dirs, %d files, totalfiles=%d" % (top, 
        #                                                        len(dirs), 
        #                                                        len(files), 
        #                                                        numfiles))
    except OSError, e:
        #print("OSError: %s" % e)
        pass
    
    if top in dirtab:
        print("%s: dir already in dirtab. Re-adding." %  top )
        CATALOGDIRS.append(top)
        numfiles = 0
    elif numfiles > maxfiles:
        print("%s: %d files > %d, creating catalogdir." % (top,
                                                           numfiles,
                                                           maxfiles))
        CATALOGDIRS.append(top)
        numfiles = 0
       
    return numfiles
               

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
        print('\n'.join(CATALOGDIRS))
        
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
    
    