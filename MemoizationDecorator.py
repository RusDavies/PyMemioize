
import functools
from PyBlakemere.PyMemoize.CacheBackend import CacheBackend
import inspect

def memoize(backend: CacheBackend, maxttl=3600, **kwargs):
    
    '''Decorator to enable a function memoization cache on functions'''

    def decorator(fn, set_kwargs=None):
        if (set_kwargs == None):
            set_kwargs = {}

        key = backend.generate_function_key( fn )

        # TODO: Is there a dryer way of expressing the following? All I really want to do
        #       is change the function signature to include self or not. 
        if (inspect.ismethod(fn)):
            @functools.wraps(fn)
            def wrapper(self, *args, **kwargs):
                unique_key = "{}_{}".format(key, backend.generate_unique_key(*args, **kwargs))
                value = backend.get( unique_key, maxttl)
                if (value is None):
                    value = fn(self, *args, **kwargs)
                    backend.set(unique_key, value, **set_kwargs)
        else:
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
    

if __name__ == '__main__':

    from PyBlakemere.PyMemoize.CacheBackendDisk import DiskCacheBackend
    from pathlib import Path

    path = Path('./.cache_test/')

    @memoize(DiskCacheBackend(path), maxttl=3600)
    def example(a, b, opts=None):
        return (a * b)

    result = example(2, 3, opts={'test': 'example'})
    print(result)

    result = example(2, 3, opts={'test': 'example'})
    print(result)
    