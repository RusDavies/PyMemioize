from os import unlink
import unittest

from MemoizationDecorator import memoize
from CacheBackendDisk import DiskCacheBackend
from pathlib import Path
import time
from datetime import datetime

class TestMemoizationDecorator(unittest.TestCase):
    # Helper function, to make deleting folders easy. 
    @staticmethod
    def delete_folder(pth):
        if (pth.exists()):
            for sub in pth.iterdir():
                if (sub.is_dir()):
                    TestMemoizationDecorator.delete_folder(sub)
                else:
                    sub.unlink()
            pth.rmdir()
        return

    def setUp(self) -> None:
        # Ensure we start eah test with a clean cache
        cache_path = Path('./.cache_test')
        TestMemoizationDecorator.delete_folder(cache_path)
        
        # Create a cache to use
        self.cache = DiskCacheBackend(cachedir=cache_path)

        return

    #@unittest.skip
    def test_memoize_function(self):

        # Define a function using the memoize decorator
        @memoize(backend=self.cache)
        def example(a, b):
            return a * b

        a = 6; b = 7
        expected = 6 * 7

        # Run for the first time
        result = example(a, b)
        self.assertEqual(result, expected)

        # Run for the second time
        result = example(a, b)
        self.assertEqual(result, expected)


    #@unittest.skip
    def test_memoize_classmethod(self):

        # Define a class with a class method using the memoize decorator
        class example_class: 
            @memoize(backend=self.cache)
            def example(self, a, b):
                return a * b

        a = 6; b = 7
        expected = 6 * 7

        # Instantiate the class
        iut = example_class()

        # Run for the first time
        result = iut.example(a, b)
        self.assertEqual(result, expected)

        # Run for the second time
        result = iut.example(a, b)
        self.assertEqual(result, expected)


    #@unittest.skip
    def test_memoize_performance(self):
        # define an expensive call
        def expensive(a):
            time.sleep(0.1)
            return a

        # Get a baseline timing
        start = datetime.now().timestamp()
        for i in range(0, 10): 
            expensive(1)
        baseline_time = datetime.now().timestamp() - start

        # Now define the memoized equivalent
        @memoize(backend=self.cache)
        def expensive_memoized(a):
            time.sleep(0.1)
            return a

        # Get a memoized timing
        start = datetime.now().timestamp()
        for i in range(0, 100): 
            expensive_memoized(1)
        memoized_time = datetime.now().timestamp() - start

        # Make sure we're within the expeccted performance envelope
        performance_ratio = memoized_time / baseline_time
        performance_ratio_threshold = 0.2
        # print('performance_ratio = {}'.format(performance_ratio))
        self.assertLessEqual( performance_ratio, performance_ratio_threshold )

        return 


    #@unittest.skip
    def test_minimal_working_example(self):
        @memoize(self.cache, maxttl=3600)
        def example(a, b, opts=None):
            return (a * b)

        result1 = example(2, 3, opts={'test': 'example'})
        result2 = example(2, 3, opts={'test': 'example'})

        self.assertEqual( result1, result2 )


if __name__ == '__main__':
    unittest.main()

