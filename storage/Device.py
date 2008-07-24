class Device(object):
    """
    Base class for browsable storage devices.
    """

    def __init__(self):
    
        pass
        
        
    def get_prefix(self):
        """
        Returns the prefix for addressing this storage device.
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
        """
    
        raise NotImplementedError
        
        
    def get_file(self, path):
        """
        Returns the File object representing the given path.
        """
    
        raise NotImplementedError
        
        
    def ls(self, path):
        """
        Returns a list of File objects representing the contents of the
        given path.
        """
    
        raise NotImplementedError
        
        
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
                    gobject.timeout_add(10, do_async, files)
            else:
                cb(None, *args)
        
        # override this by your implementation
        files = self.ls(path)
        import gobject        
        do_async(files)


    def get_fd(self, resource):
        """
        Returns a file descriptor for reading the given resource.
        This method may raise an exception to signalize failure or timeout.
        """

        raise NotImplementedError
        
        
        
    def get_resource(self, resource):
        """
        Returns the resource URI to access the given resource. Usually this
        method just returns the given resource. But sometimes (e.g. YouTube),
        this URI has to be specially determined.
        """
        
        return resource
        
