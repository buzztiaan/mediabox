"""
Class for representing a file or folder on a storage device.
"""

import hashlib
import base64
import os


class File(object):
    """
    Class for representing a file or folder on a storage device.
    Do not subclass this class.
    
    @since: 0.96
    """

    NONE =         0
    ITEMS_ENQUEUEABLE =    1 << 0
    """items in this folder can be enqueued to a list"""
    ITEMS_ADDABLE =        1 << 1
    """this folder provides an ADD button"""
    ITEMS_SORTABLE =       1 << 2
    """items in this folder can be rearranged"""
    ITEMS_UNSORTED =       1 << 3
    """items in this folder show no index letter"""
    ITEMS_COMPACT =        1 << 4
    """items in this this folder are normally viewed in a compact way"""
    


    FILE = "application/x-other"
    """MIME type for unknown file types"""

    CONFIGURATOR = "application/x-configurator"
    """MIME type for configurators"""

    DIRECTORY = "application/x-folder"
    """MIME type for folders"""
    
    DEVICE_ROOT = "application/x-device-folder"
    """MIME type for device folders"""
    

    def __init__(self, device):
        """
        Creates a new File object belonging to the given storage device.
        
        @param device: the storage device of the file
        """
    
        self.__device = device

        self.device_id = device.get_device_id()
        """
        ID of this file's device
        @since: 0.96.5
        """

        self.folder_flags = self.NONE
        """@since: 0.96.5"""
        
        
        self._LEGACY_SUPPORT_file_to_delete = None
        """ONLY FOR INTERNAL USE: support legacy plugins with delete method"""
                

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

        self.message = ""
        """
        text message displayed in the browser
        @since: 2010.06.18
        """

        self.comparable = None
        """
        property that can be used for sorting files
        @since: 2010.07.26
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

        self.thumbnailer = ""
        """
        Name of the thumbnailer component used for thumbnailing this file.
        @since: 2010.01.17
        """

        self.thumbnailer_param = None
        
        self.icon = ""
        """
        may contain the path of an icon image
        @since: 0.96.4
        """        
        
        self.frame = (None, 0, 0, 0, 0)
        """
        may contain a frame pixbuf
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


    def __cmp__(self, other):
    
        if (other):
            return cmp((self.comparable, self.name.upper(), self.full_path),
                       (other.comparable, other.name.upper(), other.full_path))
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


    def __get_bookmarked(self):

        return self.__device.get_bookmarked(self)

    def __set_bookmarked(self, v):

        self.__device.set_bookmarked(self, v)

    bookmarked = property(__get_bookmarked, __set_bookmarked)
    """
    bookmark status of the file
    @since: 0.97
    """


    def __get_md5(self):
        
        try:
            return self.__md5
        except:
            self.__md5 = hashlib.md5(self.full_path).hexdigest()
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
        
        
    def delete_file(self, f):
        """
        Deletes the given file  from this folder. This only
        works if the storage device implements the C{delete_file} method.
        @since: 2009.10.7
        """

        return self.__device.delete_file(self, f)
               
        
    def get_file_actions(self, f):
        """
        Returns a list of actions for the given file in the folder.
        @since: 2009.10
        
        @param f: file object
        @return: list of (icon, action_name, callback) tuples
        """
        
        return self.__device.get_file_actions(self, f)


    def get_bulk_actions(self):
        
        return self.__device.get_bulk_actions(self)



    def get_children(self):
        """
        Returns a list of children of this folder.
        @since: 0.96
        
        @return: list of File objects
        """
    
        import gtk
        import gobject
    
        def collector(f):
            if (f):
                collection.append(f)
            else:
                finished[0] = True
                gobject.timeout_add(0, lambda : False)
            return True
    
        finished = [False]
        collection = []
        self.get_contents(0, 0, collector)
        while (not finished[0]):
            gtk.main_iteration(True)
    
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


    def shift_file(self, pos, amount):
        """
        Shifts the file at the given position by the given amount.
        The shifting amount may be positive or negative.
        @since: 2009.10.20
        
        @param pos: index of file
        @param amount: shifting amount
        """
        
        self.__device.shift_file(self, pos, amount)
        
        
    @staticmethod
    def make_safe_name(name):
        """
        Returns a filename-safe version of the given name.
        @since: 2010.06.15
        
        @param name: a string
        @return: a string that can be safely used for a filename
        """

        replace_map = [("/", "-"),
                       ("!", ""),
                       ("*", "+"),
                       ("?", ""),
                       ("\\", "-"),
                       (":", "-")]
                       
        for a, b in replace_map:
            name = name.replace(a, b)

        return name

        
    @staticmethod
    def pack_path(prefix, *items):
        """
        Packs the given string items into a valid file path.
        @since: 2010.06.14
        
        @param prefix: path prefix
        @param items: variable list of strings
        @return: path string
        """
        
        parts = ",".join([ base64.b64encode(str(i)) for i in items ])
        return os.path.join(prefix, base64.b64encode(parts))


    @staticmethod
    def unpack_path(path):
        """
        Unpacks the given path into prefix and items.
        @since: 2010.06.14
        
        @param path: path string
        @return: tuple of path prefix and items
        """
        
        prefix = os.path.dirname(path)
        data = os.path.basename(path)
        parts = base64.b64decode(data).split(",")
        
        items = [ base64.b64decode(p) for p in parts ]
        
        return [prefix] + items

