"""
Base class of all storage devices.
"""

from com import Component, msgs
from utils import logging


class Device(Component):
    """
    Base class of all storage devices.
    Storage devices provide virtual file systems for use by MediaBox.
    New virtual file systems can be added by subclassing this base class.
    
    Storage devices belong to one of the categories
     - L{CATEGORY_CORE} - belonging to the core
     - L{CATEGORY_LOCAL} - file system for accessing local files
     - L{CATEGORY_LAN} - file system for accessing stuff on the LAN, e.g. UPnP devices
     - L{CATEGORY_WAN} - file system for accessing stuff on the internet
     - L{CATEGORY_OTHER} - file system for accessing other stuff, e.g. mobile phones
     - L{CATEGORY_HIDDEN} - hidden device not directly visible in the browser

    The category determines the position where the device will appear in the
    user interface. The list of devices is sorted first by category, then
    alphabetically.
    
    Storage devices are of type
     - L{TYPE_PRIVATE}
     - L{TYPE_GENERIC}
     - L{TYPE_AUDIO}
     - L{TYPE_VIDEO}
     - L{TYPE_IMAGE}
     
    Viewers list devices of certain types. The video viewer e.g. only lists
    devices of type L{TYPE_VIDEO}, while the devices of type L{TYPE_GENERIC}
    are listed by the folder viewer. Devices of L{TYPE_PRIVATE} are not listed
    automatically.

    Every instance of a device has a unique device ID string that is returned by
    L{get_device_id}. This is ID is used by MediaBox to keep track of devices
    being added or removed. In most cases, the device ID maybe the same as the
    device prefix.

    The device prefix is a unique string used for addressing the storage device.
    See method L{get_prefix} for details.

    @since: 0.96
    """


    CATEGORY_INDEX = 0
    CATEGORY_CORE = 1
    CATEGORY_LOCAL = 2
    CATEGORY_LAN = 3
    CATEGORY_WAN = 4
    CATEGORY_OTHER = 5
    CATEGORY_HIDDEN = 6
    
    #TYPE_PRIVATE = 0
    TYPE_GENERIC = 1
    TYPE_AUDIO = 2
    TYPE_VIDEO = 3
    TYPE_IMAGE = 4


    CATEGORY = CATEGORY_OTHER
    """category of this device"""
    TYPE = TYPE_GENERIC
    """type of this device"""


    def __init__(self):
    
        self.__bookmarks = []

        Component.__init__(self)
        
        
    def get_device_id(self):
        """
        Returns the unique device identifier.
        @since: 0.96
        
        @return: device identifier
        """
        
        return self.get_prefix()
        
        
    def get_prefix(self):
        """
        Returns the device prefix for addressing this storage device.
        This is a unique string forming the first part of URIs and is used
        for identifying the appropriate storage device implementation for a
        particular path.
        
        E.g. in case of UPnP AV content directories, this would be the
        protocol together with the UDN::
        
          upnp://uuid:898f9738-d930-4db4-a3cf-0015af8f11f6
          
        Every prefix MUST contain '://' to separate the protocol name from the
        device identifier. The protocol name must not be empty. The device
        identifier may be empty where appropriate.
        @since: 0.96
        
        @return: prefix
        """
    
        raise NotImplementedError("Device.get_prefix() must be implemented")
        
        
    def get_name(self):
        """
        Returns the human readable name of this storage device.
        @since: 0.96
        
        @return: name
        """
    
        raise NotImplementedError


    def get_icon(self):
        """
        Returns the icon for representing this storage device in a user
        interface. Returns None if no icon is available.
        @since: 0.96
        
        @return: icon pixbuf
        """
    
        return None
        
        
    def get_root(self):
        """
        Returns the File object representing the root path of the device.
        The returned path does not contain the device prefix.
        @since: 0.96
        
        @return: root file object
        """
    
        raise NotImplementedError
        
        
    def get_file(self, path):
        """
        Returns the File object represented by the given path string.
        The specified path does not contain the device prefix.
        @since: 0.96
        
        @param path: path string
        @return: file object
        """
    
        raise NotImplementedError
        
        
    def new_file(self, path):
        """
        Can be implemented by devices to support creating new files.
        @since: 0.96
        
        @param path: file object of the parent folder
        """
    
        raise NotImplementedError


    def delete_file(self, folder, idx):
        """
        Deletes the file given by its index number from the given folder.
        @since: 0.96.5
        
        @param folder: file object of the parent folder
        @param idx:    index of file to delete
        """
        
        # support legacy plugins
        logging.warning("DEPRECATED: %s implements 'delete'",
                        self.__class__.__name__)        
        self.delete(folder._LEGACY_SUPPORT_file_to_delete)

        
    def delete(self, f):
        """
        Can be implemented by devices to support deleting files.
        @since: 096
        @deprecated: use L{delete_file} instead
        
        @param f: file object to delete
        """
    
        raise NotImplementedError


    def keep(self, f):
        """
        Keeps the given file. Storage device can implement this method to
        let the user keep remote stuff locally.
        @since: 0.96
        
        @param f: file object to keep
        """
        
        raise NotImplementedError


    def swap(self, f, idx1, idx2):
        """
        Swaps two files in this folder.
        @since: 0.96.5
        
        @param idx1: index of first file
        @param idx2: index of second file
        """
        
        pass



    def ls(self, path):
        """
        Returns a list of File objects representing the contents of the
        given path.
        @since: 0.96
        @deprecated: L{get_contents} should be used instead
        
        @param path: file object to list
        @return: list of file objects
        """
    
        def cb(f, items, finished):
            if (f):
                items.append(f)
                return True
            else:
                finished[0] = True
                return False
                
        finished = [False]
        items = []
        self.ls_async(path, cb, items, finished)
        while (not finished[0]):
            pass
        return items


    def ls_async(self, path, cb, *args):
        """
        Lists the given path asynchronously by calling the given callback
        on each item. After processing every item, the implementation is
        expected to return None to signalize the end.
        @since: 0.96
        
        @param path: file object to list
        @param cb:   callback handler
        @param args: variable list of arguments to the callback handler
        """

        def do_async(files):
            if (files):
                f = files.pop(0)
                v = cb(f, *args)            
                if (v):
                    gobject.timeout_add(0, do_async, files)
                return v
            else:
                return cb(None, *args)
        
        raise SyntaxError
        # override this by your implementation
        files = self.ls(path)
        import gobject        
        do_async(files)
        
        
    def get_contents(self, path, begin_at, end_at, cb, *args):
        """
        Lists the contents of the given path asynchronously by invoking the
        given callback handler on every file. Terminates with a C{None} object.
        You can limit the result set by specifying C{begin_at} and C{end_at}.
        Pass C{0} for C{begin_at} and C{end_at} to get the whole result set.
        @since: 0.96.5
        
        @param path: file object to list
        @param begin_at: first element of the result set
        @param end_at: last element of the result set, or C{0} for no limit
        @param cb: callback handler
        @param args: variable list of arguments to the callback handler
        """
        
        def on_file(f, counter):
            if (f):
                if (end_at == 0 and begin_at <= counter[0]):
                    ret = cb(f, *args)
                elif (begin_at <= counter[0] < end_at):
                    ret = cb(f, *args)
                else:
                    ret = True
                    
                counter[0] += 1
                return ret
                
            else:
                return cb(None, *args)

        self.ls_async(path.path, on_file, [0])


    def load(self, f, maxlen, cb, *args):
        """
        Retrieves the given amount of bytes of the file asynchronously.
        
        May raise an IOError if retrieving is not supported.
        @since: 0.96
        
        @param maxlen: number of bytes to retrieve or -1 for retrieving the
                       whole file
        @param cb:     callback handler for accepting the data chunks
        @param args:   variable list of arguments to the callback handler
        """
        
        raise IOError("retrieval not supported")


    def get_resource(self, f):
        """
        Returns the resource URI to access the given resource. Usually this
        method just returns the given resource. But sometimes (e.g. YouTube),
        this URI has to be specially determined.
        @since: 0.96
        """
        
        return f.resource


    def get_bookmarked(self, f):

        if (not self.__bookmarks):
            self.__bookmarks = self.call_service(msgs.BOOKMARK_SVC_LIST, [])

        return (f in self.__bookmarks)


    def set_bookmarked(self, f, v):

        if (v):
            self.emit_message(msgs.BOOKMARK_SVC_ADD, f)
        else:
            self.emit_message(msgs.BOOKMARK_SVC_DELETE, f)


    def handle_BOOKMARK_EV_INVALIDATED(self):

        self.__bookmarks = self.call_service(msgs.BOOKMARK_SVC_LIST, [])
