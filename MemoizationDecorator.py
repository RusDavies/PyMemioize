
import functools
from PyBlakemere.PyMemoize.CacheBackend import CacheBackend
from PyBlakemere.PyMemoize.CacheBackendDiskIndexer import CacheBackendDiskIndexer
import inspect

def memoize(backend: CacheBackend, maxttl=3600, is_class_method=False, **kwargs):
    
    '''Decorator to enable a function memoization cache on functions'''

    def decorator(fn, set_kwargs=None):
        if (set_kwargs == None):
            set_kwargs = {}

        key = backend.generate_function_key( fn )

        # inspect.ismethod() doesn't work to automatically differentation class methods from raw functions
        # This is because the decorator seems to pass only the raw function without class context. 
        # For now, working around, by adding a 'is_class_method' argument to the decorator. 
        #if (inspect.ismethod(fn)):
        if (is_class_method):
            @functools.wraps(fn)
            def wrapper(self, *args, **kwargs):
                unique_key = "{}_{}".format(key, backend.generate_unique_key(*args, **kwargs))
                (hit, value) = backend.get( unique_key, maxttl)
                if (not hit): 
                    value = {'fn': fn.__name__, 'args': args, 'kwargs': kwargs}
                    value['result'] = fn(self, *args, **kwargs)
                    backend.set(unique_key, value, **set_kwargs)

                return value['result']

        else:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                unique_key = "{}_{}".format(key, backend.generate_unique_key(*args, **kwargs))
                (hit, value) = backend.get( unique_key, maxttl)
                if (not hit):  
                    value = {'args': args, 'kwargs': kwargs}
                    value['result'] = fn(*args, **kwargs)
                    backend.set(unique_key, value, **set_kwargs)
                return value['result']
        return wrapper
        
    return functools.partial(decorator, **kwargs)

    