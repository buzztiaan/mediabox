from com import Component


"""
Base class of all storage devices.
"""


class Device(Component):
    """
    Base class for browsable storage devices.
    Storage devices provide virtual file systems for use by MediaBox.
    New virtual file systems can be added by subclassing the Device base class.
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
    TYPE = TYPE_GENERIC


    def __init__(self):
    
        Component.__init__(self)
        
        
    def get_device_id(self):
        """
        Returns the unique device identifier.
        """
        
        return self.get_prefix()
        
        
    def get_prefix(self):
        """
        Returns the device prefix for addressing this storage device.
        This is a unique string forming the first part of URIs and is used
        for identifying the appropriate storage device implementation for a
        particular path.
        
        E.g. in case of UPnP AV content directories, this would be the
        protocol together with the UDN:
        
          upnp://uuid:898f9738-d930-4db4-a3cf-0015af8f11f6
          
        Every prefix MUST contain '://' to separate the protocol name from the
        device identifier. The protocol name must not be empty. The device
        identifier may be empty where appropriate.
        """
    
        raise NotImplementedError("Device.get_prefix() must be implemented")
        
        
    def get_name(self):
        """
        Returns the human readable name of this storage device.
        """
    
        raise NotImplementedError


    def get_icon(self):
        """
        Returns the icon for representing this storage device in a user
        interface. Returns None if no icon is available. 
        """
    
        return None
        
        
    def get_root(self):
        """
        Returns the File object representing the root path of the device.
        The returned path does not contain the device prefix.
        """
    
        raise NotImplementedError
        
        
    def get_file(self, path):
        """
        Returns the File object representing the given path.
        The specified path does not contain the device prefix.
        """
    
        raise NotImplementedError
        
        
    def new_file(self, path):
    
        raise NotImplementedError
        
        
    def delete(self, f):
    
        raise NotImplementedError


    def keep(self, f):
        """
        Keeps the given file. Storage device can implement this method to
        let the user keep remote stuff locally.
        """
        
        raise NotImplementedError


    def ls(self, path):
        """
        Returns a list of File objects representing the contents of the
        given path.
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
        
        @param maxlen: number of bytes to retrieve or -1 for retrieving the
                       whole file
        @param cb:     callback handler for accepting the data chunks
        @param *args:  variable list of arguments to the callback handler
        """
        
        raise IOError("retrieval not supported")


    def get_resource(self, f):
        """
        Returns the resource URI to access the given resource. Usually this
        method just returns the given resource. But sometimes (e.g. YouTube),
        this URI has to be specially determined.
        """
        
        return f.resource

