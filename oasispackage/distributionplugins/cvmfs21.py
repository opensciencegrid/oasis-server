#!/usr/bin/env python 


import commands
import datetime
import logging
import os
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

        #       #FIXME
        #       # allow re-signing from remote host
        #       
        #       masterkey = '/etc/cvmfs/keys/%s.masterkey' %self.repo
        #       # FIXME
        #       # check if masterkey file exists, and raise an exception otherwise 
        #       # for example, if this code is run at a Replica host
        #       
        #       whitelist = '/srv/cvmfs/%s/.cvmfswhitelist' %sef.repo
        #       
        #       self.log.info('Signing 7-day whitelist for repo %s  with master key...' %self.repo)
        #       
        #       now = datetime.datetime.utcnow()
        #       now_str = now.strftime('%Y%m%d%H%M%S')
        #       # this is equivalent to date -u "+%Y%m%d%H%M%S"
        #       
        #       nextweek = now + datetime.timedelta(days=7) 
        #       nextweek_str = nextweek.strftime('%Y%m%d%H%M%S')
        #       # this is equivalent to date -u --date='next week' "+%Y%m%d%H%M%S"
        #       
        #       # read the whitelist file
        #       # content of whitelist file is like this
        #       #
        #       #   ['20140325141252\n', 
        #       #    'E20140401141252\n', 
        #       #    'Nmis.opensciencegrid.org\n', 
        #       #    '4E:6C:E9:0D:92:83:F0:D5:22:82:02:CD:C5:DA:0C:E3:C1:86:74:FB\n', 
        #       #    '--\n', 
        #       #    '(stdin)= e034cf1b9f11801ffcefdbf64d04c\n', 
        #       #    '\xad\xb0\xc6g\x96....4\xc7\xdb\x\x8b@\xb5\x97Z\xd3?\x0baS\n', 
        #       #    '\x83\xd4|\x98b\xf7~\xe3\xe1E.....4r\xe6=^\xfc\xc2b7\xf1\x06']
        #       #
        #       f = open(whitelist)
        #       lines = f.readlines()
        #       content_repo = lines[2][:-1]
        #       content_fingerprint = lines[3][:-1]
        #
        #       # create a temporary unsigned file
        #       import tempfile
        #       tmpdir = tempfile.mkdtemp(dir='/tmp/')
        #       tmppath = os.path.join(tmpdir, 'unsigned') 
        #       file_unsigned = open(tmppath, 'w')
        #       print >> unsigned, now_str
        #       print >> unsigned, 'E%s' %nextweek_str
        #       print >> unsigned, 'N%s' %content_repo
        #       print >> unsigned, content_fingerprint
        #       file_unsigned.close()
        #       
        #       sha1 = commands.getoutput('cat %s | openssl sha1 | head -c40' % tmppath)
        #       file_unsigned = open(tmppath, 'a')
        #       print >> unsigned, '--'
        #       print >> unsigned, sha1
        #       file_unsigned.close()
        #
        #       path_sha1 = os.path.join(tmpdir, 'sha1')
        #       file_sha1 = open(path_sha1, 'w')
        #       print >> file_sha1, sha1, # the last comma is to avoid the trailing newline
        #       file_sha1.close()
        #       
        #       path_signature = os.path.join(tmpdir, 'signature')
        #       commands.getoutput('openssl rsautl -inkey %s -sign -in %s -out %s' %(masterkey, path_sha1, path_signature) )
        #       
        #       # add the signature to file_unsigned
        #       file_unsigned = open(tmppath, 'a')
        #       file_signature = open(path_signature)
        #       lines = file_signature.readlines()
        #       for line in lines:
        #           line = line[:-1]
        #           print >> file_unsigned, line
        #
        #       file_unsigned.close()
        #
        #       # replace old .cmvfswhitelist by new one (file_unsigned)
        #       shutil.copyfile(tmppath, whitelist)
        #
        #       # delete everything in the temporary directory
        #       shutil.rmtree(tmpdir)






    def createrepository(self):
        pass

        #   ------  VERSION IN BASH  -----------
        #
        #
        #       TMPFILE="/tmp/addosgrepo$$"
        #       trap "rm -f ${TMPFILE}" 0
        #       if ! wget -qO$TMPFILE "$1/.cvmfswhitelist"; then
        #           echo "$ME: unable to wget $1/.cvmfswhitelist" >&2
        #           exit 1
        #       fi
        #       REPONAME="`cat -v $TMPFILE|sed -n 's/^N//p'`"
        #       
        #       set -e
        #       
        #       MASTERKEY=/etc/cvmfs/keys/$STRATUM0.masterkey
        #       if [ -f $MASTERKEY ]; then
        #           # on stratum 0
        #           case "$REPONAME" in
        #           "") echo "$ME: no repository name found in $1/.cvmfswhitelist" >&2
        #               exit 1
        #               ;;
        #           *.opensciencegrid.org)
        #               ;;
        #           *)  echo "$ME: repository $REPONAME not in opensciencegrid.org" >&2
        #               exit 1
        #               ;;
        #           esac
        #           CATDIR="/srv/cvmfs/$REPONAME/pub/catalogs"
        #           su cvmfs -c "mkdir -p $CATDIR && cp $TMPFILE $CATDIR/.cvmfswhitelist"
        #           $MYDIR/resign_osg_whitelist "$REPONAME"
        #       else
        #           # on stratum 1
        #           cvmfs_server add-replica -o root $1 /etc/cvmfs/keys/opensciencegrid.org.pub
        #           rm -f /etc/httpd/conf.d/cvmfs.$REPONAME.conf
        #           # make this also look like a master because other stratum 1s
        #           #   may read from it
        #           touch /srv/cvmfs/$REPONAME/.cvmfs_master_replica
        #           # pull initial snapshot
        #           cvmfs_server snapshot $REPONAME
        #       fi
        #       
        
        
        
        
