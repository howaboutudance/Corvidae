import shelve
from rwlock import RWLock
from . import app
import os
from collections.abc import MutableMapping

class CommunityShelf(MutableMapping):
    """
    A CommunityShelf is a special kind of shelf that wraps a standard Shelf such that reads and writes are protected by a read-write lock, suitable for multi-thread operations.

    It does not inherit from shelve.Shelf because it constantly opens and closes the underlying shelf. 
    """

    def __init__(self, path):
        self.lock = RWLock()
        self.stubpath = path


    @property
    def filename(self):
        # Check that the directory it's supposed to be in exists. 
        fullpath = os.path.join(app.config["data_dir"], self.stubpath)
        bpath = os.path.basename(fullpath)
        if(not os.path.exists(bpath)):
            os.makedirs(bpath)
        if(not os.path.exists(fullpath)):
            shelve.open(fullpath, flag='c').close()
        return fullpath

    @property
    def read_shelf(self) -> shelve.Shelf:
        """
        This is a read-only version of the shelf, as used for getting arbitrary items out of the dictionary. 
        """
        return shelve.open(self.filename,flag='r')
    
    @property
    def write_shelf(self) -> shelve.Shelf:
        """ This is a writeable (and self-creating) version of the shelf, used for updating items in the shelf."""
        return Shelve.open(self.filename, flag='c')

    def read_op(func):
        """Wraps around a function such that it consumes a read lock on the shelf"""
        def read_lock_wrapper(self,*args, **kwargs):
            self.lock.reader_lock.acquire()
            ret = func(self, *args, **kwargs)
            self.lock.reader_lock.release()
            return ret
        return read_lock_wrapper
    
    def write_op(func):
        """Wraps around a function such that it consumes a write lock on the shelf. This will wait until all read locks have been released"""
        def write_lock_wrapper(self, *args, **kwargs):
            self.lock.writer_lock.acquire()
            ret = func(self,*args, **kwargs)
            self.lock.writer_lock.release()
            return ret
        return write_lock_wrapper
    
    @read_op
    def __contains__(self, key):
        return shelve.Shelf.__contains__(self.read_shelf, key)
    
    @read_op
    def __len__(self):
        return shelve.Shelf.__len__(self.read_shelf)

    @read_op
    def __iter__(self):
        return self.read_shelf.__iter__()
    

    @read_op
    def contains(self, key):
        with self.read_shelf as shelf:
            return key in shelf
    
    @read_op
    def keys(self):
        with self.read_shelf as shelf:
            return list(shelf.keys())
    
    @read_op
    def values(self):
        with self.read_shelf as shelf:
            return shelf.values()

    @read_op
    def items(self):
        with self.read_shelf as shelf:
            return list(shelf.items())

    @read_op
    def __getitem__(self, key):
        with self.read_shelf as shelf:
            if(not key in shelf):
                raise KeyError(f"Key {key} does not exist in shelf!")
            else:
                return shelf[key]
    
    @read_op
    def get(self, key, default=None):
        with self.read_shelf as shelf:
            return shelf.get(key, default)

    @write_op
    def add(self, key, value):
        with self.write_shelf as shelf:
            shelf[key] = value
    
    @write_op
    def __setitem__(self, key, value):
        with self.write_shelf as shelf:
            shelf[key] = value
            shelf.sync()
    
    @write_op
    def __delitem__(self, key):
        with self.write_shelf as shelf:
            del shelf[key]
            shelf.sync()
    
    @read_op
    def keys(self) -> list:
        return list(self.read_shelf.keys())
    
    @read_op
    def items(self) -> list:
        return list(self.read_shelf.items())
    
    @read_op
    def search(self, call_func) ->list:
        """
        A possibly long operation. This is functionally a wrapper for filter, but where the handle gets opened for longer. 
        """
        with self.read_shelf as shelf:
            return list(filter(lambda key: call_func(shelf[key]), shelf))