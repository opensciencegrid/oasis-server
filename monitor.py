#!/usr/bin/env python

#
# tool to inspect a remote CVMFS DB
# original code is from Rene Meusel (rene.meusel@cern.ch)
# with some modifications from Jose Caballero (jcaballero@bnl.gov)
#

import getopt

import cvmfs
import sys


class Stats:
    def __init__(self, catalog):
        self.regular_files = self._count_regular(catalog)
        self.directories   = self._count_directories(catalog)
        self.symlinks      = self._count_symlinks(catalog)
        self.data_volume   = self._count_data_volume(catalog)
        self.nested_clgs   = catalog.nested_count()

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


def compute_stat(repo, catalog):
    print >> sys.stderr, "computing statistics for" , catalog.revision , catalog.hash , catalog.root_prefix
    stats = Stats(catalog)
    for nested in catalog.list_nested():
        nested_stats = get_stat_from_hash(repo, nested.hash)
        stats.add(nested_stats)
    return stats


stat_cache_ = {}
def get_stat_from_hash(repo, catalog_hash):
    if catalog_hash in stat_cache_:
        print >> sys.stderr, "cache hit for" , catalog_hash
        return stat_cache_[catalog_hash]

    catalog = repo.retrieve_catalog(catalog_hash)
    stats = compute_stat(repo, catalog)
    stat_cache_[catalog_hash] = stats
    repo.close_catalog(catalog)

    return stats


root_catalog = repo.retrieve_root_catalog()
while True:
    stats = compute_stat(repo, root_catalog)
    print root_catalog.revision , root_catalog.last_modified , root_catalog.hash , stats.regular_files , stats.directories , stats.symlinks , stats.data_volume , stats.nested_clgs
    new_root_catalog = repo.retrieve_catalog(root_catalog.previous_revision)
    repo.close_catalog(root_catalog)
    root_catalog = new_root_catalog


class Repository(object):

    def __init__(self, url, port, repositoryname):

        self.url = url
        self.port = port
        self.repositoryname = repositoryname
        self.repositoryURI = '%s:%s/cvmfs/%s' %(self.url, self.port, self.repositoryname)

        self.repository = cvmfs.open_repository(self.repositoryURI)



def main(options):

    # DEFAULTS #
    port = '8000'

    opts, args = getopt.getopt(options, '', ['url=', 'port=', 'repositoryname='])
    
    for k,v in opts:
        if k == '--url':
            url = v
        if k == '--port':
            port = v
        if k == '--repositoryname':
            repositoryname = v

    repository = Repository(url, port, repositoryname)


if __name__ == '__main__':
    rc = main(sys.argv[1:])
    sys.exit(rc)



#    some modifications on my own to the script from Rene
#
#
#        first_revision = 40
#        last_revision = 50
#        
#        while True:
#        
#            revision = root_catalog.revision
#            if int(revision) < first_revision:
#                break
#            elif int(revision) > last_revision:
#                pass
#            else:
#                stats = compute_stat(repo, root_catalog)
#                print root_catalog.revision , root_catalog.last_modified , root_catalog.hash , stats.regular_files , stats.directories , stats.symlinks , stats.data_volume , stats.nested_clgs
#
#            new_root_catalog = repo.retrieve_catalog(root_catalog.previous_revision)
#            repo.close_catalog(root_catalog)
#            root_catalog = new_root_catalog
#        
