from mediabox import values
from utils import logging

import os


_INDEX_FILE = os.path.join(values.USER_DIR, "files.idx")

# when the index format becomes incompatible, raise the magic number to force
# rejection of old index
_MAGIC = 0xbeef0002


_NUMBER_OF_FIELDS = 4


class FileIndex(object):
    """
    Class for a persistable file index, because a SQL database would be overkill
    and calls for trouble.
    """

    ROOT = 0
    STATUS = 1
    MIMETYPE = 2
    SCANTIME = 3

    STATUS_NEW = 0
    STATUS_REMOVED = 1
    STATUS_UNCHANGED = 2
    STATUS_UNCONFIRMED = 3
    

    def __init__(self):
    
        self.__is_dirty = False
    
        # table: fullpath -> [fields]
        self.__index = {}
        
        self.__load_index()
        
        
    def __load_index(self):

        try:
            import cPickle
            fd = open(_INDEX_FILE, "rb")
        except:
            return
            
        try:
            magic, data = cPickle.load(fd)
        except:
            logging.error(logging.stacktrace())
            return
        finally:
            fd.close()

        # ignore the file if it isn't compatible
        if (magic == _MAGIC):
            self.__index = data
            self.__is_dirty = False
        
        
        
    def __save_index(self):
    
        self.__is_dirty = False
        try:
            import cPickle
            fd = open(_INDEX_FILE, "wb")
        except:
            return
            
        try:
            cPickle.dump((_MAGIC, self.__index), fd, 2)
        except:
            pass
        finally:
            fd.close()
        
        
    def set_field(self, field, key, value):
    
        self.__is_dirty = True
        if (not key in self.__index):
            self.__index[key] = [None] * _NUMBER_OF_FIELDS
        self.__index[key][field] = value
        
        
    def get_field(self, field, key):
    
        try:
            return self.__index[key][field]
        except KeyError:
            return None
    
        
        
        
    def get_new_files(self):

        if (self.__is_dirty): self.__save_index()
        
        files = [ fp for fp in self.__index
                  if self.get_field(self.STATUS, fp) == self.STATUS_NEW ]
        return files

        
        
    def get_removed_files(self):

        if (self.__is_dirty): self.__save_index()

        files = [ fp for fp in self.__index
                  if self.get_field(self.STATUS, fp) == self.STATUS_REMOVED ]
        return files
        
        
    def get_unchanged_files(self):

        if (self.__is_dirty): self.__save_index()

        files = [ fp for fp in self.__index
                  if self.get_field(self.STATUS, fp) == self.STATUS_UNCHANGED ]
        return files


        
    def get_files_of_root(self, root):

        files = []
        for fp in self.__index:
            if (self.get_field(self.ROOT, fp) == root):
                files.append(fp)
        #end for
        
        return files    
    
    
    def get_mimetype(self, fp):
    
        return self.get_field(self.MIMETYPE, fp)
    
        
    def has_file(self, fp):
    
        if (fp in self.__index):
            return (self.get_field(self.STATUS, fp) != self.STATUS_REMOVED)
        else:
            return False
        
        
    def get_roots(self):
    
        roots = []
        for fp in self.__index:
            root = self.get_field(self.ROOT, fp)
            if (not root in roots):
                roots.append(root)
        #end for
        
        return roots    
        
        
    def clear_status(self):
    
        self.__is_dirty = True
        for fp in self.__index.keys()[:]:
            status = self.get_field(self.STATUS, fp)
            if (status == self.STATUS_REMOVED):
                del self.__index[fp]
            else:
                self.set_field(self.STATUS, fp, self.STATUS_UNCHANGED)
        #end for


    def clear(self):
    
        self.__is_dirty = True
        self.__index.clear()

