#!/usr/bin/env python 


import commands
import datetime
import logging
import os
import shutil
import time


# ----------------------------------------------------------------------------
#
# FIXME !!
#
# allow the cvmfs server to be a remote host:
#
#       -- the cmfs_server transaction and publish command with ssh
#
#       -- the rsync command with either remote ssh access or rsync access
#
# ----------------------------------------------------------------------------


from oasispackage.interfaces import BaseDistribution

class cvmfs21(BaseDistribution):


    def __init__(self, project):

        super(cvmfs21, self).__init__(project)

        #self.log = logging.getLogger("cvmfs")
        self.log.debug('init of cvmfs21 plugin')

        # self.project.dest is like  /cvmfs/myvo.opensciencegrid.org
        # the repo is the <myvo.opensciencegrid.org> part
        self.repo = self.project.destdir.split('/')[2]


    def transfer(self):

        self.log.info('transfering files from %s to %s' %(self.project.srcdir, self.project.destdir))

        ## cmd = 'cvmfs_server transaction %s' %self.repo
        # example:   cvmfs_server transaction atlas.opensciencegrid.org
        cmd = 'sudo -u %s cvmfs_server transaction %s' %(self.project.destdiruser, self.repo)
        self.log.info('command = %s' %cmd)


        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('interaction with cvmfs server failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
            return st

        ## cmd = 'rsync -a -l --delete %s/ %s' %(self.project.srcdir, self.project.destdir)
        # example:   rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        cmd = 'sudo -u %s rsync --stats -a -l --delete %s/ %s' %(self.project.destdiruser, self.project.srcdir, self.project.destdir)
        self.log.info('command = %s' %cmd)

        # FIXME
        #  perhaps parsing the output of rsync --stats instead of 
        #  logging the entire output???
        #   
        #       # rsync --stats ...
        #   
        #       Number of files: 2
        #       Number of files transferred: 1
        #       Total file size: 0 bytes
        #       Total transferred file size: 0 bytes
        #       Literal data: 0 bytes
        #       Matched data: 0 bytes
        #       File list size: 31
        #       File list generation time: 0.001 seconds
        #       File list transfer time: 0.000 seconds
        #       Total bytes sent: 82
        #       Total bytes received: 34
        #       
        #       sent 82 bytes  received 34 bytes  232.00 bytes/sec
        #       total size is 0  speedup is 0.00
        #       

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('transferring files failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
            return st

        return st

    def publish(self):
        
        rc = self._publish()
        if rc:
            self.log.critical('publishing failed. Aborting.')
            return rc

        return 0

    def _publish(self):

        self.log.info('publishing CVMFS for repository %s' %self.repo)

        ## cmd = 'cvmfs_server publish %s' %self.repo 
        # example:   cvmfs_server publish atlas.opensciencegrid.org
        cmd = 'sudo -u %s cvmfs_server publish %s' %(self.project.destdiruser, self.repo)
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('publishing failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st
    
    def resign(self):
        '''
        Re-sign the .cvmfswhitelist of a  given repository
        '''
        return 0 

        # FIXME: TEST THE FOLLOWING CODE 


        #FIXME: allow re-signing from remote host
        
        masterkey = '/etc/cvmfs/keys/%s.masterkey' %self.repo
        # FIXME
        # check if masterkey file exists, and raise an exception otherwise 
        # for example, if this code is run at a Replica host
        
        whitelist = '/srv/cvmfs/%s/.cvmfswhitelist' %sef.repo
        
        self.log.info('Signing 7-day whitelist for repo %s  with master key...' %self.repo)
        
        now = datetime.datetime.utcnow()
        now_str = now.strftime('%Y%m%d%H%M%S')
        # this is equivalent to date -u "+%Y%m%d%H%M%S"
        
        nextweek = now + datetime.timedelta(days=7) 
        nextweek_str = nextweek.strftime('%Y%m%d%H%M%S')
        # this is equivalent to date -u --date='next week' "+%Y%m%d%H%M%S"
        
        # read the whitelist file
        # content of whitelist file is like this
        #
        #   ['20140325141252\n', 
        #    'E20140401141252\n', 
        #    'Nmis.opensciencegrid.org\n', 
        #    '4E:6C:E9:0D:92:83:F0:D5:22:82:02:CD:C5:DA:0C:E3:C1:86:74:FB\n', 
        #    '--\n', 
        #    '(stdin)= e034cf1b9f11801ffcefdbf64d04c\n', 
        #    '\xad\xb0\xc6g\x96....4\xc7\xdb\x\x8b@\xb5\x97Z\xd3?\x0baS\n', 
        #    '\x83\xd4|\x98b\xf7~\xe3\xe1E.....4r\xe6=^\xfc\xc2b7\xf1\x06']
        #
        f = open(whitelist)
        lines = f.readlines()
        content_repo = lines[2][:-1]
        content_fingerprint = lines[3][:-1]
        
        # create a temporary unsigned file
        import tempfile
        tmpdir = tempfile.mkdtemp(dir='/tmp/')
        path_new_whitelist = os.path.join(tmpdir, 'whitelist') 
        f_new_whitelist = open(path_new_whitelist, 'w')
        print >> f_new_whitelist, now_str
        print >> f_new_whitelist, 'E%s' %nextweek_str
        print >> f_new_whitelist, 'N%s' %content_repo
        print >> f_new_whitelist, content_fingerprint
        f_new_whitelist.close()
        
        sha1 = commands.getoutput('cat %s | openssl sha1 | head -c40' % path_new_whitelist)
        f_new_whitelist = open(path_new_whitelist, 'a')
        print >> f_new_whitelist, '--'
        print >> f_new_whitelist, sha1
        f_new_whitelist.close()
        
        path_sha1 = os.path.join(tmpdir, 'sha1')
        f_sha1 = open(path_sha1, 'w')
        print >> f_sha1, sha1, # the last comma is to avoid the trailing newline
        f_sha1.close()
        
        path_signature = os.path.join(tmpdir, 'signature')
        commands.getoutput('openssl rsautl -inkey %s -sign -in %s -out %s' %(masterkey, path_sha1, path_signature) )
        
        # add the signature to file_unsigned
        f_new_whitelist = open(path_new_whitelist, 'a')
        f_signature = open(path_signature)
        lines = f_signature.readlines()
        for line in lines[:-1]: # all lines except the last one
            line = line[:-1]
            print >> f_new_whitelist, line
        print >> f_new_whitelist, lines[-1],  # print last line, but this one without newline character at the end
        
        f_new_whitelist.close()
        
        # replace old .cmvfswhitelist by new one (file_unsigned)
        shutil.copyfile(path_new_whitelist, whitelist)
        
        # delete everything in the temporary directory
        shutil.rmtree(tmpdir)




    def createrepository(self):

        commands.getoutput('cvmfs_server mkfs -o %s %s' %(self.project.destdiruser, self.repo))


    def shouldlock(self, listflagfiles):
        '''
        it should lock only if any of the flagfiles belongs to the same project
        '''
        # FIXME: should I pay attention to the <status> field???
        for flagfile in listflagfiles;
            if flagfile.startswith(self.project.projectname):
                return True
        return False


   
