import unittest

from PyBlakemere.PyMemoize.CacheBackendDisk import DiskCacheBackend
from pathlib import Path

# Helper function, to make deleting folders easy. 
# TODO: Move this into a utility library
def delete_folder(pth):
    if (pth.exists()):
        for sub in pth.iterdir():
            if (sub.is_dir()):
                delete_folder(sub)
            else:
                sub.unlink()
        pth.rmdir()
    return

class TestDiskCacheBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._cache_path = Path('./test/.TestDiskCacheBackend_cache/')

    def setUp(self) -> None:
        delete_folder(self._cache_path)
        return


    @unittest.skip
    def test_constructor(self):
        # When we instantiate the DiskCacheBackend, we should get a non-None object returned without exception
        iut = DiskCacheBackend(cachedir=self._cache_path)
        self.assertIsNotNone(iut)


    #@unittest.skip
    def test_set_and_get(self):
        # When we set an object, we expect a filename with the specified key to appear in the cache directory
        test_data = {'test': [1, 2, 3], 'simple': 42}
        key = 'test_set'
        expected_file = self._cache_path / key

        # Ensure that the file does NOT exist
        self.assertFalse( expected_file.exists() )

        # Instantiate the cache
        iut = DiskCacheBackend(cachedir=self._cache_path)

        # Write the data to cache        
        iut.set(key, test_data)

        # Ensure that the file does now exist
        self.assertTrue( expected_file.exists() )

        # Recover the data
        (has_result, result) = iut.get(key)
        self.assertTrue( has_result )
        self.assertIsNotNone( result )
        self.assertEqual(2, len(result) )
        self.assertIsNotNone(result.get('test',   None) )
        self.assertIsNotNone(result.get('simple', None) )

        # Ensure that the file does still exist
        self.assertTrue( expected_file.exists() )



    #@unittest.skip
    def test_set_and_get_encrypted(self):
        # When we set an object, we expect a filename with the specified key to appear in the cache directory
        test_data = {'test': [1, 2, 3], 'simple': 42}
        key = 'test_set'
        path = self._cache_path / key

        # Ensure that the files do NOT exist
        self.assertFalse( path.exists() )

        # Instantiate the cache
        iut = DiskCacheBackend(cachedir=self._cache_path, encrypt_at_rest=True, encryption_password='123456789')

        # Write the data to cache        
        iut.set(key, test_data)

        # Ensure that the encrypted file and only the encrypted file now exists
        self.assertTrue( path.exists()   )

        # Recover the data
        (has_result, result) = iut.get(key)
        self.assertTrue( has_result )
        self.assertIsNotNone( result )
        self.assertEqual(2, len(result) )
        self.assertIsNotNone(result.get('test',   None) )
        self.assertIsNotNone(result.get('simple', None) )

        # Ensure that the file still exists
        self.assertTrue( path.exists() )


if __name__ == '__main__':
    unittest.main()
