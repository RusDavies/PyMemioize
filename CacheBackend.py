#import sys
#import os
import hashlib
import json

#
# Abstract base class for the caching backend 
class CacheBackend(object):

    ''' Abstract base class for RusPyMemioze caching backends'''

    def get(self,key, fallback=None):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError


    @staticmethod
    def hasher(val):
        result = None
        
        # If we have a list (which is unhashable) then cast it to a tuple
        if (isinstance(val, list)):
            val = tuple(val)

        # If we have a dictonary, we json.dumps it
        if (isinstance(val, dict)):
            val = json.dumps(val)

        return hash(val)
    

    @staticmethod
    def generate_unique_key(*args, **kwargs):

        # Hash the args
        hashed_args = []
        for item in args:
            hashed_args.append( str(CacheBackend.hasher(item)) ) 

        # Hash the kwargs
        ## We're seeing lists in the kawgs, which aren't hashable. 
        hashed_kwargs = [] 
        for (key, val) in kwargs.items():
            hashed_key = str(CacheBackend.hasher(key))
            hashed_val = str(CacheBackend.hasher(val))          
            hashed_kwargs.append( '{}_{}'.format(hashed_key, hashed_val))

        # Rehash to avoid overly large hashes
        hashed_kwargs = hashlib.md5(':'.join(hashed_args + hashed_kwargs).encode('utf-8')).hexdigest()         
        
        return hashed_kwargs

    @staticmethod
    def generate_function_key(fn):
        raise NotImplementedError

        # FIXME: CacheBackend.generage_function_key(...) doesn't work. For now we're making 'key' a mandatory field in the decorator, to avoid extracting a function key. 
        # if (type(fn) is 'function'):
        #     return hashlib.md5(fn.__qualname__).hexdigest()
        # else:
        #     raise Exception('Not a function')


# DONE: Write a cache backend for filesystems. See CacheBackendDisk.py
# TODO: Write a cache backend for in-memory
# TODO: Write a cache backend for Redis
# TODO: Write a cache backed for Memcached
