#import os
import pickle 
import time
from PyBlakemere.PyMemoize.CacheBackend import CacheBackend
from pathlib import Path
from datetime import datetime


#
# Concrete inmemory-based cache
class InMemoryCacheBackend(CacheBackend):
    
    '''Concrete in-memory implementation of CacheBackend'''

    def __init__(self, globalmaxttl:int=3600, autopurge=True, autopurgecount=100):
        self._autopurge = autopurge
        self._autopurgecount = autopurgecount
        self._autopurgecount_remaining = autopurgecount

        self._globalmaxttl = globalmaxttl
        self._cache = {}


    def set(self, key, item):
        timestamp = datetime.now().timestamp
        self.cache[key] = (timestamp, item)
        self._autopurge()


    def get(self, key, localttl=-1):
        has_result = False
        result = None

        self._autopurge()

        (timestamp, item)  = self._cache.get(key, (False, None))

        ttl_limit = localttl if (localttl >= 0) else  self._globalmaxttl

        if (timestamp != False):
            age = datetime.now().timestamp() - timestamp
            if ( age <= ttl_limit):
                result = item
                has_result = True

        return (has_result, result)


    def _autopurge(self):
        if (self._autopurge != False):
            self._autopurgecount_remaining = self._autopurgecount_remaining - 1
            if (self._autopurgecount_remaining <= 0):
                self.purge()
                self._autopurgecount_remaining = self._autopurgecount 
        return


    def purge(self, purge_all: bool=False, localttl=-1):

        timestamp_reference = datetime.now().timestamp()
        ttl_limit = localttl if (localttl >= 0) else  self._globalmaxttl

        if (purge_all):
            self._cache = {}
        else:
            purged_cache = { key: (timestamp, item) for (key,(timestamp, item)) in self.cache.values() if timestamp - timestamp_reference > ttl_limit }
            self._cache = purged_cache

        return       