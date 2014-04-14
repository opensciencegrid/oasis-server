#!/usr/bin/env python 

import commands
from base import BaseProbe


class nodelete(BaseProbe):
    """
    check is some file has been deleted
    and react accordingly
    
    Config variables for this probe are

        apply_to_directory
        level

    It uses rsync to compare the scratch area with /cvmfs/ area
    Example of rsync output is 

        $ rsync -ani --delete <src_dir> <dest_dir>
        .d..t...... ./
        *deleting   foo.sh
        *deleting   bar.conf
        >f+++++++++ bar2.py
        
        It says two files have been deleted
    """

    def __init__(self, vo, conf, section):

        super(nodelete, self).__init__(vo, conf, section)

        self.directory = conf.get(section, "apply_to_directory") 
        self.level = conf.get(section, "level")


    def run(self):

        self.log.debug('calling probe <nodelete> for vo %s and directory %s' %(self.vo, self.directory))

        cmd = 'rsync -ani --delete %s/ouser.%s/src/%s /cvmfs/oasis.opensciencegrid.org/%s/%s' %(self.scratch, self.vo, self.directory, self.vo, self.directory)
        out = commands.getoutput(cmd)       

        # check is out contains the pattern *deleting
        n_deleted = 0
        for line in out.split('\n'):
            if line.startswith('*deleting'):
                n_deleted += 1

        if n_deleted:
            if self.level == "warning":
                self.log.warning('%s files have been deleted underneath directory %s' %(n_deleted, self.directory))
                return 0       
            if self.level == "abort":
                self.log.critical('%s files have been deleted underneath directory %s. Abort.' %(n_deleted, self.directory))
                return 1
        else:
            self.log.info('No files have been deleted underneath directory %s' %self.directory)
            return 0


