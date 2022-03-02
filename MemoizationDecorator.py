
import functools
from PyMemoize.CacheBackend import CacheBackend

# TODO: Figure out how to have only one decorator that works for both non-class functions and class methods.
# TODO: Add a named parameter to each decorator, allowing the 'exists in cache' check to be skipped (force refresh) 

def cache_function_factory(backend: CacheBackend, key=None, maxttl=3600, **kwargs):
    
    '''Decorator to enable a function memoization cache on non-class functions'''

    if (key is None or len(key) == 0):
        #key = backend.generate_function_key( fn )
        raise Exception('key must not be None or zero length')

    def decorator(fn, set_kwargs=None):
        if (set_kwargs == None):
            set_kwargs = {}

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            unique_key = "{}_{}".format(key, backend.generate_unique_key(*args, **kwargs))
            value = backend.get( unique_key, maxttl)
            if (value is None):
                value = fn(*args, **kwargs)
                backend.set(unique_key, value, **set_kwargs)

            return value
        return wrapper
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


if __name__ == '__main__':

    from PyMemoize.CacheBackendDisk import DiskCacheBackend

    cbe = DiskCacheBackend('./.cache_test/')

    @cache_function_factory(cbe, key='test_', maxttl=36)
    def example(a, b, opts=None):
        return (a * b)


    result = example(2, 3, opts={'test': 'example'})
    result = example(2, 3, opts={'test': 'example'})



    