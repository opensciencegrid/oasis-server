#!/usr/bin/env python 

'''
create .catalogdirs in root of cmvfs scratch area
maximum files per catalog =  100000
CVMFS is supposed to deal with new *and removed* .cvmfscatalog files during a publishing attempt. 
Catalogs should contain between 1000 and 200,000 files. 

Need to do depth-first, *postorder* traversal of tree. 

for node in root:
    process all children
    process root
    


'''
import getopt
import os
import stat
import sys

#from posix import *
#try:
#    from posix import _exit
#except ImportError:
#    pass
#import posixpath as path


(libpath,tail) = os.path.split(sys.path[0])
#print(libpath)
nlibpath = os.path.split(libpath)[0]
print(nlibpath)
print(tail)
sys.path.append(nlibpath)

#from oasispackage.interfaces import BaseProbe

def mywalk(top):
    '''
    postorder, depth-first processing (alphabetical)
    recursively determine how many files in subtree
    
    takes current catalog 
    
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
            numfiles += mywalk(dirpath)
        numfiles = len(files) + numfiles
        print("%s: %s dirs, %d files, totalfiles=%d" % (top, 
                                                                len(dirs), 
                                                                len(files), 
                                                                numfiles))
    except OSError, e:
        print("OSError: %s" % e)
    return numfiles
    
     
            
        

#class makecatalogdirs(BaseProbe):
class makecatalogdirs(object):

    def __init__(self, oasisproberootdir="/var", oasisprobedestdir="/var"):
        self.rootdir = oasisproberootdir
        self.destdir = oasisprobedestdir

    def run(self):
        print("src = %s dest = %s" % (self.rootdir, self.destdir))
        
        running_total = 0
        absolute_total = 0
        
        mywalk(self.rootdir)
        
        #for root, dirs, files in mywalk(self.rootdir, topdown=False, onerror=None, followlinks=False):
        #    print(root)
        #    print(" %s" % dirs)
        #    print(" %d files" % len(files))
            


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

"""
    # Handle command line options
    rootdir = "/var"
    destdir = "/var"


    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvr:t:", 
                                   ["help",
                                    "debug",
                                    "verbose", 
                                    "rootdir=", 
                                    "destdir=", 
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
                    
    probe = makecatalogdirs( oasisproberootdir=rootdir, oasisprobedestdir=destdir )
    rc = probe.run() 
    sys.exit(rc)
    
    