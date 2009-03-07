"""
Base class of all storage devices.
"""

from com import Component


class Device(Component):
    """
    Base class of all storage devices.
    Storage devices provide virtual file systems for use by MediaBox.
    New virtual file systems can be added by subclassing the Device base class.
    
    Storage devices belong to one of the categories L{CATEGORY_CORE},
    L{CATEGORY_LOCAL}, L{CATEGORY_LAN}, L{CATEGORY_WAN}, or L{CATEGORY_OTHER}.
    The category determines the position where the device will appear in the
    user interface. The list of devices is sorted first by category, then
    alphabetically.
    
    Storage devices are of type L{TYPE_GENERIC}, L{TYPE_AUDIO}, L{TYPE_VIDEO},
    or L{TYPE_IMAGE}. Viewers list devices of certain types. The video viewer
    e.g. only lists devices of type L{TYPE_VIDEO}, while the devices of type
    L{TYPE_GENERIC} are listed by the folder viewer.

    @since: 0.96
    """


    CATEGORY_CORE = 0
    CATEGORY_LOCAL = 1
    CATEGORY_LAN = 2
    CATEGORY_WAN = 3
    CATEGORY_OTHER = 4
    
    TYPE_GENERIC = 0
    TYPE_AUDIO = 1
    TYPE_VIDEO = 2
    TYPE_IMAGE = 3


    CATEGORY = CATEGORY_OTHER
    """category of this device"""
    TYPE = TYPE_GENERIC
    """type of this device"""


    def __init__(self):
    
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
        Returns the File object representing the given path.
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
        
        
    def delete(self, f):
        """
        Can be implemented by devices to support deleting files.
        @since: 096
        
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


    def ls(self, path):
        """
        Returns a list of File objects representing the contents of the
        given path.
        @since: 0.96
        @deprecated: L{ls_async} should be used instead
        
        @param path: file object to list
        @return: list of file objects
        """
    
        def cb(f, items, finished):
            if (f):
                items.append(f)
            else:
                finished[0] = True
                
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
                if (not v):
                    return
                else:
                    gobject.timeout_add(0, do_async, files)
            else:
                cb(None, *args)
        
        # override this by your implementation
        files = self.ls(path)
        import gobject        
        do_async(files)


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

