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
from oasispackage.distributionplugins.cvmfs import cvmfs
import  oasispackage.utils

class cvmfs21(cvmfs):


    def __init__(self, project):

        super(cvmfs21, self).__init__(project)

        self.log = logging.getLogger("logfile.cvmfs21")
        self.log.debug('init of cvmfs21 plugin')

    # --------------------------------------------------------------------
    #           transfer
    # --------------------------------------------------------------------

    def transfer(self):
        """
        transfer files from user scratch area to CVMFS filesystem.
        Steps:

            1. start a transaction section
            examples:   
                $ cvmfs_server transaction atlas.opensciencegrid.org
                $ sudo -u ouser.atlas cvmfs_server transaction atlas.opensciencegrid.org

            2. copy, with rsync, data from the user scratch area
            example:   
                $ rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
                $ sudo -u ouser.atlas rsync -a -l --delete /home/atlas /cvmfs/atlas.opensciencegrid.org
        
        """

        self.log.info('transfering files from %s to %s' %(self.src, self.dest))

        rc, out = self._starttransaction()
        if rc != 0:
            return rc, out
        rc, out = self._transfer()
        return rc, out
       
    def _starttransaction(self): 

        cmd = 'sudo -u %s cvmfs_server transaction %s' %(self.project.repository_dest_owner, self.project.repositoryname)
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('interaction with cvmfs server failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st, out

    def _transfer(self):
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

        cmd = 'sudo -u %s rsync --stats -a -l --delete %s/ %s' %(self.project.project_dest_owner, self.src, self.dest)
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('transferring files failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)

        return st, out

    # --------------------------------------------------------------------
    #       publish
    # --------------------------------------------------------------------

    def publish(self):
        """
        publish the CVMFS repo.
        example:   
            $ cvmfs_server publish atlas.opensciencegrid.org
        """
        
        rc, out = self._publish()
        if rc:
            self.log.critical('publishing failed. Aborting.')

        return rc, out

    def _publish(self):

        self.log.info('publishing CVMFS for repository %s' %self.project.repositoryname)

        cmd = 'sudo -u %s cvmfs_server publish %s' %(self.project.repository_dest_owner, self.project.repositoryname)
        self.log.info('command = %s' %cmd)

        st, out = commands.getstatusoutput(cmd)
        if st:
            self.log.critical('publishing failed.')
            self.log.critical('RC = %s' %st)
            self.log.critical('output = %s' %out)
        return st, out
    
    # --------------------------------------------------------------------
    #       adminstrative methods
    # --------------------------------------------------------------------

    def resign(self):
        '''
        Re-sign the .cvmfswhitelist of a  given repository
        '''
        return 0 

        # FIXME: TEST THE FOLLOWING CODE 


        #FIXME: allow re-signing from remote host
        
        masterkey = '/etc/cvmfs/keys/%s.masterkey' %self.project.repositoryname
        # FIXME
        # check if masterkey file exists, and raise an exception otherwise 
        # for example, if this code is run at a Replica host
        
        whitelist = '/srv/cvmfs/%s/.cvmfswhitelist' %self.project.repositoryname
        
        self.log.info('Signing 7-day whitelist for repo %s  with master key...' %self.project.repositoryname)
        
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
        '''
        create the repo area in CVMFS 2.1
        example:
            $ service httpd start; cvmfs_server mkfs -o ouser.atlas atlas.opensciencegrid.org 
        '''
 
        self.log.info('creating repository %s' %self.project.repositoryname)
        self.addrepositoryuser()
        if self.checkrepository():
            self.log.info('repository %s already exists' %self.project.repositoryname)
            return 0
        else:
            rc, out = commands.getstatusoutput('service httpd start; cvmfs_server mkfs -o %s %s' %(self.project.repository_dest_owner, self.project.repositoryname))
            self.log.info('rc = %s, out=%s' %(rc,out))
            if rc != 0:
                self.log.critical('creating repository %s failed.' % self.project.repositoryname)
            return rc

    def createproject(self):
        '''
        create the project area in CVMFS 2.1
        Example:
            $ sudo -u ouser.osg cvmfs_server transaction osg.opensciencegrid.org
            $ mkdir /cvmfs/osg.opensciencegrid.org/bio/
            $ chown ouser.bio:ouser.bio /cvmfs/osg.opensciencegrid.org/bio/
            $ cvmfs_server publish osg.opensciencegrid.org

        NOTE: we only create a project directory if 
              the CVMFS repo is not already in transaction
              (someone else is publishing)

        NOTE: we only need to create a project directory if 
              it is different that the repo directory
        '''

        self.log.info('creating project %s' %self.project.projectname)
        self.addprojectuser()
        if self.checkproject():
            self.log.info('project %s already exists' %self.project.projectname)
            return 0
        else: 
            rc = self.createrepository()
            if rc != 0:
                self.log.critical('creating repository %s failed. Aborting' % self.project.repositoryname)
                return rc

            if self._intransaction():
                self.log.info('the repository %s is currently in a transaction session. Aborting.' %self.project.repositoryname)
                raise Exception('the repository %s is currently in a transaction session. Aborting.' %self.project.repositoryname)

            if self.project.project_dest_dir == "":
                self.log.info('the project destination directory is the same that the repository destination directory. Nothing to do')
                return 0
            else:
                rc, out = commands.getstatusoutput('sudo -u %s cvmfs_server transaction %s' %(self.project.repository_dest_owner, self.project.repositoryname))
                rc, out = commands.getstatusoutput('mkdir %s; chown %s:%s %s'  %(self.dest, self.project.project_dest_owner, self.project.project_dest_owner, self.dest))
                self._publish()
                return rc


    def _intransaction(self):
        '''
        checks if the CVMFS repo is already in transaction 
        (someone else is publishing)
        '''
        return os.path.isdir('/var/spool/cvmfs/%s/in_transaction' %self.project.repositoryname)


    def shouldlock(self, listflagfiles):
        '''
        it should lock only if any of the flagfiles belongs to the same repository
        listflagfiles is a list of flagfiles as paths 
        '''
        # FIXME: should I pay attention to the <status> field???
        for flagfile in listflagfiles:
            flagfile = os.path.basename(flagfile)
            ###if flagfile.startswith(self.project.projectname):
            ###    return True

            flagfile_projectname = flagfile.split('.')[0]   #FIXME: this should be a method of FlagFile class
            # check if flagfile_projectname belongs to the same repo
            # that current projectname
            if self.project.repository(flagfile_projectname) == self.project.repository():
                return True

        return False


    def addprojectuser(self):
        '''
        creates the UNIX ID
        '''
        return oasispackage.utils.adduser(self.project.project_dest_owner)


    def addrepositoryuser(self):
        '''
        creates the UNIX ID
        '''
        return oasispackage.utils.adduser(self.project.repository_dest_owner)
