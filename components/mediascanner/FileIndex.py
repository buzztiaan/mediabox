from mediabox import values
from utils import logging

import os
import time


_INDEX_FILE = os.path.join(values.USER_DIR, "files.idx")

# when the index format becomes incompatible, raise the magic number to force
# rejection of old index
_MAGIC = 0xbeef0004


_NUMBER_OF_FIELDS = 4


class FileIndex(object):
    """
    Class for a persistable file index, because a SQL database would be overkill
    and calls for trouble.
    """

    # available fields
    ROOT = 0
    STATUS = 1
    MIMETYPE = 2
    SCANTIME = 3

    # available states of file entries
    STATUS_NEW = 0
    STATUS_REMOVED = 1
    STATUS_UNCHANGED = 2
    STATUS_UNCONFIRMED = 3
    

    def __init__(self):

        # time of the last scan
        self.__scantime = 0
    
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
        """
        Returns a list of all files that have been added since the previous
        scan.
        @since: 0.96
        
        @return: list of file paths
        """

        if (self.__is_dirty): self.__save_index()
        
        files = [ fp for fp in self.__index
                  if self.get_field(self.STATUS, fp) == self.STATUS_NEW ]
        return files

        
        
    def get_removed_files(self):
        """
        Returns a list of all files that have been removed since the previous
        scan.
        @since: 0.96
        
        @return: list of file paths
        """

        if (self.__is_dirty): self.__save_index()

        files = [ fp for fp in self.__index
                  if self.get_field(self.STATUS, fp) == self.STATUS_REMOVED ]
        return files
        
        
    def get_unchanged_files(self):
        """
        Returns a list of all files that have been untouched since the previous
        scan.
        @since: 0.96
        
        @return: list of file paths
        """
        
        if (self.__is_dirty): self.__save_index()

        files = [ fp for fp in self.__index
                  if self.get_field(self.STATUS, fp) == self.STATUS_UNCHANGED ]
        return files


        
    def get_files_of_root(self, root):
        """
        Returns a list of all files currently below the given media root.
        @since: 0.96
        
        @param root: path of media root
        @return: list of file paths
        """
        

        files = []
        for fp in self.__index:
            if (self.get_field(self.ROOT, fp) == root):
                files.append(fp)
        #end for
        
        return files    
    
    
    def get_mimetype(self, fp):
        """
        Returns the MIME type of the given file as stored in the index.
        @since: 0.96
        
        @param fp: file path
        @return: MIME type string
        """
    
        return self.get_field(self.MIMETYPE, fp)
    
        
    def has_file(self, fp):
        """
        Returns whether the given file is currently available.
        @since: 0.96
        
        @param fp: file path
        @return: C{True} or C{False}
        """
    
        if (fp in self.__index):
            return (self.get_field(self.STATUS, fp) != self.STATUS_REMOVED)
        else:
            return False
        
        
    def get_roots(self):
        """
        Returns a list of all media roots that have indexed files in them.
        @since: 0.96
        
        @return: list of media roots
        """
    
        roots = []
        for fp in self.__index:
            root = self.get_field(self.ROOT, fp)
            status = self.get_field(self.STATUS, fp)
            if (status != self.STATUS_REMOVED and not root in roots):
                roots.append(root)
        #end for
        
        return roots    
        
        
    def clear_status(self):
        """
        Clears the status field of all entries and removes entries that have
        been marked as removed. This action has to be taken before initiating
        a new scan.
        @since: 0.96
        """
    
        self.__is_dirty = True
        for fp in self.__index.keys()[:]:
            status = self.get_field(self.STATUS, fp)
            if (status == self.STATUS_REMOVED):
                del self.__index[fp]
            else:
                self.set_field(self.STATUS, fp, self.STATUS_REMOVED)
        #end for
        
        self.__scan_time = int(time.time())


    def clear(self):
        """
        Clears the index, wiping it completely empty.
        @since: 0.96
        """
    
        self.__is_dirty = True
        self.__index.clear()


    def discover_file(self, mediaroot, fp, mtime, mimetype):
        """
        Discovers the given file.
        @since: 2009.10.10
        
        @param mediaroot: media root of the file
        @param fp: full path of the file
        @param mtime: modification time of the file
        @param mimetype: MIME type of the file
        """

        needs_update = False
        
        if (not fp in self.__index):
            # case 1: file is completely new
            self.set_field(self.STATUS, fp, self.STATUS_NEW)
            needs_update = True
            
        elif (mtime > self.__scan_time):
            # case 2: file has been changed since last scan
            self.set_field(self.STATUS, fp, self.STATUS_NEW)
            needs_update = True
            
        else:
            # case 3: file hasn't been touched and is still there
            self.set_field(self.STATUS, fp, self.STATUS_UNCHANGED)

        if (needs_update):
            self.set_field(FileIndex.ROOT, fp, mediaroot)
            self.set_field(FileIndex.MIMETYPE, fp, mimetype)
            self.set_field(FileIndex.SCANTIME, fp, self.__scan_time)

