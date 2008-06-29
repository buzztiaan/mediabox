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


    def get_fd(self, resource):
        """
        Returns a file descriptor for reading the given resource.
        This method may raise an exception to signalize failure or timeout.
        """
    
        raise NotImplementedError
        