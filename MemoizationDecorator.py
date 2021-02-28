
import functools
from RusPyMemoize.CacheBackend import CacheBackend

# TODO: Figure out how to have only one decorator that works for both non-class functions and class methods.

def cache_function(backend: CacheBackend, key=None, maxttl=3600, **kwargs):
    
    '''Decorator to enable a function memoization cache on non-class functions'''

    if (key is None or len(key) == 0):
        #key = backend.generate_function_key( fn )
        raise Exception('key must not be None or zero length')

    def decorator(fn, set_kwargs=None):
        if (set_kwargs == None):
            set_kwargs = {}

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            unique_key = "{}_{}".format(key, backend.generate_unique_key(*args, **kwargs))
            value = backend.get( unique_key, maxttl)
            if (value is None):
                value = fn(*args, **kwargs)
                backend.set(unique_key, value, **set_kwargs)

            return value
        return inner
    return functools.partial(decorator, **kwargs)
    

def cache_class_method(backend: CacheBackend, key=None, maxttl=3600, **kwargs):
    
    '''Decorator to enable a function memoization cache on class methods'''

    if (key is None or len(key) == 0):
        #key = backend.generate_function_key( fn )
        raise Exception('key must not be None or zero length')

    def decorator(fn, set_kwargs=None):
        if (set_kwargs == None):
            set_kwargs = {}

        @functools.wraps(fn)
        def inner(self, *args, **kwargs):
            unique_key = "{}_{}".format(key, backend.generate_unique_key(*args, **kwargs))
            value = backend.get( unique_key, maxttl)
            if (value is None):
                value = fn(self, *args, **kwargs)
                backend.set(unique_key, value, **set_kwargs)

            return value
        return inner
    return functools.partial(decorator, **kwargs)
