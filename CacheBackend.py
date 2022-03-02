import hashlib
import json
import numbers

# TODO: Write a cache backend for in-memory
# TODO: Write a cache backend for Redis
# TODO: Write a cache backed for Memcached

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
        if (isinstance(val, list)):
            # Lists are unhashable. Convert to tuple
            val = tuple(val)

        elif (isinstance(val, dict)):
            # dicts are unhashable. Convert to string. 
            # TODO: json.dumps adds possibly significant overhead. Something more efficient? Perhaps 'frozenset' ?
            val = json.dumps(val)

        elif(isinstance(val, numbers.Number)):
            # Numbers seem to hash as themselves. Convert to string. 
            val = str(val)

        return str(hash(val))
    

    @staticmethod
    def generate_unique_key(*args, **kwargs):

        # Hash the args
        hashed_args = []
        for item in args:
            hashed_args.append( CacheBackend.hasher(item) ) 
        #hashed_args = CacheBackend.hasher(args)

        # Hash the kwargs
        hashed_kwargs = [] 
        for (key, val) in kwargs.items():
            hashed_key = CacheBackend.hasher(key)
            hashed_val = CacheBackend.hasher(val)          
            hashed_kwargs.append( '{}_{}'.format(hashed_key, hashed_val))

        # Rehash to avoid overly large hashes
        hashed_kwargs = hashlib.md5(':'.join(hashed_args + hashed_kwargs).encode('utf-8')).hexdigest()         
        
        return hashed_kwargs


    @staticmethod
    def generate_function_key(fn):
        if (not callable(fn)):
            raise Exception('Not a function')

        return hashlib.md5(fn.__qualname__.encode('ascii')).hexdigest()


