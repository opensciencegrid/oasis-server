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


class Info(object):
    def __init__(self, stats, catalog):
        '''
        pass an Stats object and a catalog object
        '''
       
        self.revision = catalog.revision
        self.last_modified = catalog.last_modified
        self.hash = catalog.hash
        self.regular_files = stats.regular_files
        self.directories = stats.directories
        self.symlinks = stats.symlinks
        self.data_volume = stats.data_volume
        self.nested_catalogs = stats.nested_clgs





def compute_stat(repo, catalog):  # FIXME
    print >> sys.stderr, "computing statistics for" , catalog.revision , catalog.hash , catalog.root_prefix
    stats = Stats(catalog)  # FIXME
    for nested in catalog.list_nested():
        nested_stats = get_stat_from_hash(repo, nested.hash)
        stats.add(nested_stats)
    return stats


stat_cache_ = {}
def get_stat_from_hash(repo, catalog_hash):  # FIXME
    if catalog_hash in stat_cache_:
        print >> sys.stderr, "cache hit for" , catalog_hash
        return stat_cache_[catalog_hash]

    catalog = repo.retrieve_catalog(catalog_hash)
    stats = compute_stat(repo, catalog)  
    stat_cache_[catalog_hash] = stats
    repo.close_catalog(catalog)

    return stats




class RepositoryHandler(object):

    def __init__(self, repositoryname, url=None, port=None):

        self.url = url
        self.port = port
        self.repositoryname = repositoryname
        if self.url and self.port:
            self.repositoryURI = '%s:%s/cvmfs/%s' %(self.url, self.port, self.repositoryname)
        else:
            self.repositoryURI = '/cvmfs/%s' %self.repositoryname
        

        self.repository = cvmfs.open_repository(self.repositoryURI)

        #self.stats = Stats()  #FIXME


    def get(self, first_revision=0, last_revision=0, last_n_revisions=0, revision=0):

        info = []

        root_catalog = self.repository.retrieve_root_catalog()

        current_revision = int(root_catalog.revision)

        if revision:
            revisions_range = [revision]
        elif last_n_revisions:
            revisions_range = range(current_revision - last_n_revisions + 1, current_revision + 1)
        else:
            if first_revision and not last_revision:
                revisions_range = [first_revision, current_revision + 1]
            elif not first_revision and last_revision:
                revisions_range = [1, last_revision + 1]
            elif first_revision and last_revision:
                revisions_range = [first_revision, last_revision + 1]
            else:
                return 1 
            
        while True:

            if current_revision > revisions_range[-1]:
                pass
            elif current_revision < revisions_range[0]:
                break
            else:

                stats = compute_stat(self.repository, root_catalog) 
                info.append(Info(stats, root_catalog))

            try:
                new_root_catalog = self.repository.retrieve_catalog(root_catalog.previous_revision)
                self.repository.close_catalog(root_catalog)
                root_catalog = new_root_catalog
                current_revision = root_catalog.revision
            except:
                pass  #FIXME

            return info
        


def main(options):

    # DEFAULTS #
    url = None
    port = None 
    first_revision = 0
    last_revision = 0
    last_n_revisions = 0
    revision = 0

    opts, args = getopt.getopt(options, '', ['url=', 'port=', 'repositoryname=', 'first_revision=', 'last_revision=', 'last_n_revisions=', 'revision='])
    
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
        if k == '--revision':
            revision = int(v)

    repositoryhandler = RepositoryHandler(repositoryname, url, port)
    repositoryhandler.get(first_revision, last_revision, last_n_revisions, revision)


if __name__ == '__main__':
    rc = main(sys.argv[1:])
    sys.exit(rc)



