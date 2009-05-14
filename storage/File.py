"""
Class for representing a file or folder on a storage device.
"""

import md5


class File(object):
    """
    Class for representing a file or folder on a storage device.
    Do not subclass this class.
    
    @since: 0.96
    """

    NONE =         0
    ITEMS_ENQUEUEABLE =    1 << 0
    ITEMS_SKIPPABLE =      1 << 1
    ITEMS_DELETABLE =      1 << 2
    ITEMS_BULK_DELETABLE = 1 << 3
    INDEXABLE =            1 << 4
    ITEMS_DOWNLOADABLE =   1 << 5
    ITEMS_ADDABLE =        1 << 6
    ITEMS_SORTABLE =       1 << 7
    


    FILE = "application/x-other"
    """MIME type for unknown file types"""

    DIRECTORY = "application/x-folder"
    """MIME type for folders"""
    

    def __init__(self, device):
        """
        Creates a new File object belonging to the given storage device.
        
        @param device: the storage device of the file
        """
    
        self.__device = device


        self.folder_flags = self.NONE
        """@since: 0.96.5"""
        
        
        self._LEGACY_SUPPORT_file_to_delete = None
        """ONLY FOR INTERNAL USE: support legacy plugins with delete method"""
        
        self.can_skip = False
        """
        whether the user may skip files (previous/next) in this folder
        @since: 0.96
        @deprecated: use L{folder_flags} instead
        """

        self.can_add_to_library = False
        """
        whether the user may add this folder to the library
        @since: 0.96
        @deprecated: use L{folder_flags} instead
        """

        self.can_add = False
        """
        whether the user may add items to this folder
        @since: 0.96
        @deprecated: use L{folder_flags} instead
        """
        
        self.can_delete = False
        """
        whether the user may delete this file
        @since: 0.96
        @deprecated: use L{folder_flags} instead
        """

        self.can_keep = False
        """
        whether the user may keep this non-local file
        @since: 0.96
        @deprecated: use L{folder_flags} instead
        """

        self.can_download = False
        """
        whether the user may download this file
        @since: 0.96
        @deprecated: use L{folder_flags} instead
        """

        self.is_local = False
        """
        whether this file is local
        @since: 0.96
        """
                

        self.path = ""
        """
        virtual path of the file on the device
        @since: 0.96
        """

        self.name = ""
        """
        name of the file presented to the user
        @since: 0.96
        """
        
        self.acoustic_name = ""
        """
        name of the file when read to the user
        @since: 0.96.5
        """

        self.info = ""
        """
        some info text
        @since: 0.96
        """
        
        self.description = ""
        """
        text for further description
        @since: 0.96
        """

        self.index = 0
        """
        index number that can be used for sorting
        @since: 0.96
        """

        self.parent = ""
        """
        name of parent folder, if any (can be used for grouping items)
        @since: 0.96
        """

        self.thumbnail = ""
        """
        may contain the URI of an image that can be used to generate a thumbnail
        @since: 0.96
        """
        
        self.icon = ""
        """
        may contain the path of an icon image (deprecated) or a pixbuf that can
        be used instead of a thumbnail. the image should be of a proper size
        @since: 0.96.4
        """

        self.mimetype = self.FILE
        """
        MIME type of the file
        @since: 0.96
        """
               
        self.resource = ""
        """
        URI for accessing the actual file, if any
        @since: 0.96
        """

        self.mtime = 0
        """
        Modification time of this file.
        @since: 0.96.5
        """
        
        self.__medium = None
        
        self.child_count = 0
        self.emblem = None
        


    def __cmp__(self, other):
    
        if (other):
            return cmp((self.index, self.name.upper(), self.full_path),
                       (other.index, other.name.upper(), other.full_path))
        else:
            return 1


    def __repr__(self):
        """
        Returns a readable representation of this File for debugging purposes.
        
        @return: readable representation
        """
    
        return "<" + self.full_path + ">"


    def __get_full_path(self):
    
        return self.__device.get_prefix() + self.path
        
    full_path = property(__get_full_path)
    """
    read-only: full virtual path of the file
    @since: 0.96
    """
    
    
    def __get_source_icon(self):
    
        return self.__device.get_icon()
        
    source_icon = property(__get_source_icon)
    """
    read-only: pixbuf icon representing the source device
    @since: 0.96
    """


    def __get_md5(self):
        
        try:
            return self.__md5
        except:
            self.__md5 = md5.new(self.full_path).hexdigest()
            return self.__md5

    md5 = property(__get_md5)
    """
    read-only: MD5 sum for uniquely identifying the file internally
    @since: 0.96
    """

    

    def __set_thumbnail_md5(self, v):
    
        self.__thumbnail_md5 = v
        

    def __get_thumbnail_md5(self):
    
        try:
            return self.__thumbnail_md5
        except:
            return self.md5

    thumbnail_md5 = property(__get_thumbnail_md5, __set_thumbnail_md5)
    """
    read-write: MD5 sum for uniquely identifying the file's thumbnail preview,
    if the C{md5} property shouldn't be used
    @since: 0.96
    """


    def __get_medium(self):
    
        if (self.__medium): return self.__medium
        
        uri = self.resource
        
        if (not self.is_local):
            return None
        
        elif (not uri.startswith("/")):
            return None
            
        else:
            try:
                mounts = open("/proc/mounts", "r").readlines()
            except:
                return None
            
            longest = ""
            blacklist = ["/sys", "/proc", "/dev"]
            for line in mounts:
                parts = line.split()
                mountpoint = parts[1]
                
                if (mountpoint in blacklist):
                    continue
                
                elif (uri.startswith(mountpoint)):
                    if (len(mountpoint) > len(longest)):
                        longest = mountpoint
            #end for
            self.__medium = longest
            return longest or None
        #end if
        
        return None

    medium = property(__get_medium)
    """
    read-only: path (mount point) of the medium where the file is on
    (local files only)
    @since: 0.96.3
    """
       
        
    def new_file(self):
        """
        Creates a new file in this folder. This only works if the storage
        device implements the C{new_file} method.
        @since: 0.96
        
        @return: the new File object
        """
    
        return self.__device.new_file(self)
        
        
    def delete_file(self, idx):
        """
        Deletes the file given by the index number from this folder. This only
        works if the storage device implements the C{delete_file} method.
        @since: 0.96.5
        """

        return self.__device.delete_file(self, idx)    
        
        
    def delete(self):
        """
        Deletes this file. This only works if the storage device implements
        the delete method.
        @since: 0.96
        @deprecated: use L{delete_file} instead
        """

        return self.__device.delete(self)
        
        
    def get_children(self):
        """
        Returns a list of children of this folder.
        @since: 0.96
        @deprecated: L{get_children_async} should be used instead
        
        @return: list of File objects
        """
    
        def collector(f):
            if (f):
                collection.append(f)
            else:
                finished[0] = True
            return True
    
        finished = [False]
        collection = []
        self.get_children_async(collector)
        while (not finished[0]):
            import gtk
            gtk.main_iteration(False)
    
        return collection


    def get_children_async(self, cb, *args):
        """
        Lists the children of this folder asynchronously by invoking the
        given callback handler on every file. Terminates with a None object.
        @since: 0.96
        @deprecated: L{get_contents} should be used instead.
        
        @param cb: callback handler
        @param args: variable list of arguments to the callback handler
        """
        
        self.__device.get_contents(self, 0, 0, cb, *args)
        
        
    def get_contents(self, begin_at, end_at, cb, *args):
        """
        Lists the contents of this folder asynchronously by invoking the given
        callback handler on every file. Terminates with a C{None} object.
        You can limit the result set by specifying C{begin_at} and C{end_at}.
        Pass C{0} for C{begin_at} and C{end_at} to get the whole result set.
        
        Not all devices may support limiting the result set.
        
        @since: 0.96.5
        
        @param begin_at: first element of the result set
        @param end_at: last element of the result set, or C{0} for no limit
        @param cb: callback handler
        @param args: variable list of arguments to the callback handler
        """
        
        self.__device.get_contents(self, begin_at, end_at, cb, *args)


    def load(self, maxlen, cb, *args):
        """
        Retrieves the given amount of bytes of the file asynchronously.
        
        May raise an IOError if retrieving is not supported.
        @since: 0.96
        
        @param maxlen: number of bytes to retrieve or -1 for retrieving the
                       whole file
        @param cb:     callback handler for accepting the data chunks
        @param args:  variable list of arguments to the callback handler
        """
        
        self.__device.load(self, maxlen, cb, *args)


        
    def get_resource(self):
    
        return self.__device.get_resource(self)
        
        
    def keep(self):
        """
        Instructs the storage device to keep this file. This method can be used
        for keeping a local copy of a remote file. This only works if the
        storage device implements the keep method.
        @since: 0.96
        """
    
        self.__device.keep(self)


    def swap(self, idx1, idx2):
        """
        Swaps two files in this folder.
        @since: 0.96.5
        
        @param idx1: index of first file
        @param idx2: index of second file
        """
        
        self.__device.swap(self, idx1, idx2)

