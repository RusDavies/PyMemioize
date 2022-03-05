#import sys
import os
import pickle 
import time
#import functools
from PyBlakemere.PyMemoize.CacheBackend import CacheBackend
from pathlib import Path

# TODO: Convert fully to pathlib. 

#
# Concrete disk-based cache
class DiskCacheBackend(CacheBackend):
    
    '''Concrete disk-based implementation of RusPyMemoization.CacheBackend'''

    def __init__(self, cachedir:str='~/.local/tmp/cache/memoization/general', globalmaxttl:int=3600):
        self._cachedir = Path(cachedir)
        self._globalmaxttl = globalmaxttl

        # Make sure the cachedir exists
        self._cachedir.expanduser() 
        if (not self._cachedir.exists() ):
            os.makedirs( cachedir )

        # Clean up any stale files as we start up
        self.purge()


    def set(self, key, item):
        path = os.path.join(self._cachedir, key)
        with open( path, "wb") as file:
            pickle.dump(item, file)


    def get(self, key, localttl=-1):
        has_result = False
        result = None
        path = self._cachedir / key  

        maxttl = localttl if (localttl >= 0) else self._globalmaxttl

        if (path.exists()):
            age = time.time() - os.path.getctime(path)
            if ( age <= maxttl ):
                with open(path, "rb") as f:
                    result = pickle.load(f)
                has_result = True
            else:
                path.unlink() 

        return (has_result, result)


    def __contains__(self, key):
        result = False
        path = self._cachedir / key
        if (path.exists()):
            result = True
        return result


    def purge(self, purge_all: bool=False, localttl=-1):
        files = [ f for f in os.listdir(self._cachedir) if os.path.isfile(os.path.join(self._cachedir, f))]
        t = time.time()
        for f in files:
            path = os.path.join(self._cachedir, f)
            age = t - os.path.getmtime(path)
            if (purge_all == True or ( age > self._globalmaxttl) or ( localttl >= 0 and age >= localttl)):
                os.remove( path )
       