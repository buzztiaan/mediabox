"""
Class for representing a file or folder on a storage device.
"""

import md5


class File(object):
    """
    Class for representing a file or folder on a storage device.
    Do not subclass this class.
    """

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


        self.can_skip = False
        """whether the user may skip files (previous/next) in this folder"""

        self.can_add_to_library = False
        """whether the user may add this folder to the library"""

        self.can_add = False
        """whether the user may add items to this folder"""
        
        self.can_delete = False
        """whether the user may delete this file"""

        self.can_keep = False
        """whether the user may keep this non-local file"""

        self.can_download = False
        """whether the user may download this file"""

        self.is_local = False
        """whether this file is local"""
                

        self.path = ""
        """virtual path of the file on the device"""

        self.name = ""
        """name of the file presented to the user"""

        self.info = ""
        """some info text"""
        
        self.description = ""
        """text for further description"""

        self.index = 0
        """index number that can be used for sorting"""

        self.parent = ""
        """name of parent folder, if any (can be used for grouping items)"""

        self.thumbnail = ""
        """may contain the URI of a thumbnail image"""
        
        self.mimetype = self.FILE
        """MIME type of the file"""
               
        self.resource = ""
        """URI for accessing the file"""

        
        self.__medium = None
        
        self.child_count = 0
        self.emblem = None
        


    def __cmp__(self, other):
    
        if (other):
            return cmp((self.index, self.name, self.resource),
                       (other.index, other.name, other.resource))
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
    """read-only: full virtual path of the file"""
    
    
    def __get_source_icon(self):
    
        return self.__device.get_icon()
        
    source_icon = property(__get_source_icon)
    """read-only: pixbuf icon representing the source device"""


    def __get_md5(self):
        
        try:
            return self.__md5
        except:
            self.__md5 = md5.new(self.full_path).hexdigest()
            return self.__md5

    md5 = property(__get_md5)
    """read-only: MD5 sum for uniquely identifying the file internally"""

    

    def __set_thumbnail_md5(self, v):
    
        self.__thumbnail_md5 = v
        

    def __get_thumbnail_md5(self):
    
        try:
            return self.__thumbnail_md5
        except:
            return self.md5

    thumbnail_md5 = property(__get_thumbnail_md5, __set_thumbnail_md5)
    """read-write: MD5 sum for uniquely identifying the file's thumbnail preview"""


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
            for line in mounts:
                parts = line.split()
                mountpoint = parts[1]
                if (uri.startswith(mountpoint)):
                    if (len(mountpoint) > len(longest)):
                        longest = mountpoint
            #end for
            self.__medium = longest
            return longest or None
        #end if
        
        return None

    medium = property(__get_medium)
    """read-only: path of the medium where the file is on (local files only)"""
       
        
    def new_file(self):
        """
        Creates a new file in this folder. This only works if the storage
        device implements the new_file method.
        
        @return: the new File object
        """
    
        return self.__device.new_file(self.path)
        
        
    def delete(self):
        """
        Deletes this file. This only works if the storage device implements
        the delete method.
        """
    
        return self.__device.delete(self)
        
        
    def get_children(self):
        """
        Returns a list of children of this folder.
        @deprecated: L{get_children_async} should be used instead
        
        @return: list of File objects
        """
    
        return self.__device.ls(self.path)


    def get_children_async(self, cb, *args):
        """
        Lists the children of this folder asynchronously by invoking the
        given callback handler on every file. Terminates with a None object.
        
        @param cb: callback handler
        @param args: variable list of arguments to the callback handler
        """
        
        self.__device.ls_async(self.path, cb, *args)


    def load(self, maxlen, cb, *args):
        """
        Retrieves the given amount of bytes of the file asynchronously.
        
        May raise an IOError if retrieving is not supported.
        
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
        """
    
        self.__device.keep(self)

