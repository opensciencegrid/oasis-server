#!/usr/bin/env python

#
# tool to inspect a remote CVMFS DB
# original code is from Rene Meusel (rene.meusel@cern.ch)
# with some modifications from Jose Caballero (jcaballero@bnl.gov)
#

import getopt
import sys

import cvmfs
import sys


class Stats:
    def __init__(self, catalog):
        self.regular_files = self._count_regular(catalog)
        self.directories   = self._count_directories(catalog)
        self.symlinks      = self._count_symlinks(catalog)
        self.data_volume   = self._count_data_volume(catalog)
        self.nested_clgs   = catalog.nested_count()

        self.stat_cache_ = {}

    def __str__(self):
        return "Regular:      " + str(self.regular_files) + "\n" + \
               "Directories:  " + str(self.directories)   + "\n" + \
               "Symlinks:     " + str(self.symlinks)      + "\n" + \
               "Data:         " + str(self.data_volume)   + "\n" + \
               "Nested Clgs:  " + str(self.nested_clgs)

    def add(self, nstats):
        self.regular_files += nstats.regular_files
        self.directories   += nstats.directories
        self.symlinks      += nstats.symlinks
        self.data_volume   += nstats.data_volume
        self.nested_clgs   += nstats.nested_clgs

    def _count_regular(self, catalog):
        return self._count(catalog, "SELECT count(*) FROM catalog WHERE flags & 4 AND NOT flags & 8;")

    def _count_directories(self, catalog):
        return self._count(catalog, "SELECT count(*) FROM catalog WHERE flags & 1;")

    def _count_symlinks(self, catalog):
        return self._count(catalog, "SELECT count(*) FROM catalog WHERE flags & 8;")

    def _count_data_volume(self, catalog):
        return self._count(catalog, "SELECT ifnull(sum(size), 0) FROM catalog WHERE flags & 4 AND NOT flags & 8;")

    def _count(self, catalog, query):
        result = catalog.run_sql(query)
        return result[0][0]


def compute_stat(repo, catalog):  # FIXME
    print >> sys.stderr, "computing statistics for" , catalog.revision , catalog.hash , catalog.root_prefix
    stats = Stats(catalog)  # FIXME
    for nested in catalog.list_nested():
        nested_stats = self.get_stat_from_hash(repo, nested.hash)
        stats.add(nested_stats)
    return stats


def get_stat_from_hash(repo, catalog_hash):  # FIXME
    if catalog_hash in self.stat_cache_:
        print >> sys.stderr, "cache hit for" , catalog_hash
        return self.stat_cache_[catalog_hash]

    catalog = repo.retrieve_catalog(catalog_hash)
    stats = compute_stat(repo, catalog)  
    self.stat_cache_[catalog_hash] = stats
    repo.close_catalog(catalog)

    return stats




class RepositoryHandler(object):

    def __init__(self, url, port, repositoryname):

        self.url = url
        self.port = port
        self.repositoryname = repositoryname
        self.repositoryURI = '%s:%s/cvmfs/%s' %(self.url, self.port, self.repositoryname)

        self.repository = cvmfs.open_repository(self.repositoryURI)

        self.stats = Stats()  #FIXME


    def get(self, first_revision=-1, last_revision=-1, last_n_revisions=-1):

        root_catalog = repo.retrieve_root_catalog()



        if first_revision == -1: 
        
        if last_revision == -1: 

        if last_n_revisions == -1:   # NOTE: last_n_revisions == 1 means the latest revision


        while True:
       
            # FIXME:  put the corresponding code in a try-except block
 
            revision = root_catalog.revision
            if int(revision) < first_revision:
                break
            elif int(revision) > last_revision:
                pass
            else:
                stats = compute_stat(repo, root_catalog) 
                print root_catalog.revision , root_catalog.last_modified , root_catalog.hash , stats.regular_files , stats.directories , stats.symlinks , stats.data_volume , stats.nested_clgs

            new_root_catalog = repo.retrieve_catalog(root_catalog.previous_revision)
            repo.close_catalog(root_catalog)
            root_catalog = new_root_catalog
        


def main(options):

    # DEFAULTS #
    port = '8000'
    first_revision = -1
    last_revision = -1
    last_n_revisions = -1

    opts, args = getopt.getopt(options, '', ['url=', 'port=', 'repositoryname=', 'first_revision=', 'last_revision=', 'last_n_revisions=='])
    
    for k,v in opts:
        if k == '--url':
            url = v
        if k == '--port':
            port = v
        if k == '--repositoryname':
            repositoryname = v
        if k == '--first_revision':
            first_revision = int(v)
        if k == '--last_revision':
            last_revision = int(v)
        if k == '--last_n_revisions':
            last_n_revisions = int(v)

    repositoryhandler = RepositoryHander(url, port, repositoryname)
    repositoryhandler.get(first_revision, last_revision, last_n_revisions)


if __name__ == '__main__':
    rc = main(sys.argv[1:])
    sys.exit(rc)



