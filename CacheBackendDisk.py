import os
import pickle 
import time
from PyBlakemere.PyMemoize.CacheBackend import CacheBackend
from pathlib import Path
import pyAesCrypt
import io

from Crypto.Cipher import AES
#from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

# Ref:
# - Encryption: https://www.pycryptodome.org/en/latest/src/examples.html#encrypt-data-with-aes

# TODO: Convert fully to pathlib. 
# FIXME: Do encryption in memory, to avoid any unencrypted file hitting the disk!  

#
# Concrete disk-based cache
class DiskCacheBackend(CacheBackend):
    
    '''Concrete disk-based implementation of RusPyMemoization.CacheBackend'''

    def __init__(self, cachedir:str='~/.local/tmp/cache/memoization/general', globalmaxttl:int=3600, 
                maintain_index=True, encrypt_at_rest=False, encryption_password=None, salt='abcd'):

        self._cachedir = Path(cachedir)
        self._globalmaxttl = globalmaxttl
        self._encrypt_at_rest = encrypt_at_rest

        if (self._encrypt_at_rest):
            if (not encryption_password):
                raise ValueError('encryption_password must be set when encrypt_at_rest is True')

            if (len(encryption_password) < 8):
                raise ValueError('encryption_password must be at least 8 characters long')
            
            self._ecyption_password = encryption_password
            #key = PBKDF2(encryption_password, salt.encode('ascii'), dkLen=32)
            #self.cipher = AES.new(key, AES.MODE_EAX)

        self._cachedir.expanduser() 
        cachedir.mkdir(parents=True, exist_ok=True)

        # self.indexer = None
        # if(maintain_index):
        #     self.indexer = CacheBackendDiskIndexer(CacheBackendDiskIndexer(cache_path=cachedir))

        # Clean up any stale files as we start up
        self.purge()


    def set(self, key, item):
        # Make sure the cache dir hasn't vanished 
        self._cachedir.mkdir(parents=True, exist_ok=True)

        path = self._cachedir / key

        # FIXME: Encyrpt in memory! 

        with open( path, "wb") as file:
            pickle.dump(item, file, pickle.HIGHEST_PROTOCOL)

        if (self._encrypt_at_rest):
            path_tmp = Path(str(path) + '.tmp')
            pyAesCrypt.encryptFile(path, path_tmp, self._ecyption_password)
            path.unlink()
            path_tmp.rename(path)

        return

    def get(self, key, localttl=-1):
        # Make sure the cache dir hasn't vanished 
        self._cachedir.mkdir(parents=True, exist_ok=True)

        has_result = False
        result = None
        path = self._cachedir / key
        
        maxttl = localttl if (localttl >= 0) else self._globalmaxttl

        if (path.exists()):
            age = time.time() - os.path.getctime(path)
            if ( age <= maxttl ):
                if (self._encrypt_at_rest):
                    path_tmp = Path(str(path) + '.tmp')
                    pyAesCrypt.decryptFile(path, path_tmp, self._ecyption_password)
                    path = path_tmp
                
                with open(path, "rb") as file:
                    result = pickle.load(file)
                has_result = True
                
                if (self._encrypt_at_rest):
                    path_tmp.unlink()

            else:
                path.unlink() 

        return (has_result, result)

    
    # def set(self, key, item):
    #     path = self._cachedir / key

    #     with open( path, "wb") as file:
    #         if (self._encrypt_at_rest):
    #             pickleStream = pickle.dumps(item)
    #             pyAesCrypt.encryptStream(fIn=pickleStream, fOut=file, passw=self._cipher)
    #         else:
    #             pickle.dump(item, file)

    #     return

    # def get(self, key, localttl=-1):
    #     has_result = False
    #     result = None
    #     path = self._cachedir / key
        
    #     maxttl = localttl if (localttl >= 0) else self._globalmaxttl

    #     if (path.exists()):
    #         age = time.time() - os.path.getctime(src)
    #         if ( age <= maxttl ):
    #             with open(path, "rb") as file:
    #                 if (self._encrypt_at_rest):
    #                     pickleStream = pickle.loads(file)
    #                     pyAesCrypt.decryptStream(pickleStream, path, self._encyption_cipher)
    #                 else:
    #                     result = pickle.load(f)
    #             has_result = True
                
    #             if (self._encrypt_at_rest):
    #                 unencrypted_path.unlink()

    #         else:
    #             src.unlink() 

    #     return (has_result, result)

    # def set(self, key, item):
    #     path = self._cachedir / key

    #     if (self._encrypt_at_rest):
    #         item = self.cipher.encrypt(bytes(item))

    #     with open( path, "wb") as file:
    #         pickle.dump(item, file)

    #     return



    # def get(self, key, localttl=-1):
    #     has_result = False
    #     result = None
    #     path = self._cachedir / key
        
    #     maxttl = localttl if (localttl >= 0) else self._globalmaxttl

    #     if (path.exists()):
    #         age = time.time() - os.path.getctime(path)
    #         if ( age <= maxttl ):
    #             with open(path, "rb") as f:
    #                 result = pickle.load(f)
    #             has_result = True

    #             if(self._encrypt_at_rest):
    #                 result = self.AES.decrypt(result)

    #         else:
    #             path.unlink() 

    #     return (has_result, result)      



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
       