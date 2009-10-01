from Component import Component
import msgs


class Thumbnailer(Component):
    """
    Base class for Thumbnailer components. Thumbnailers handle creating
    thumbnails of files.
    @since: 2009.10
    """

    def __init__(self):
    
        Component.__init__(self)
        
        
    def get_mime_types(self):
        """
        Returns supported MIME types as a list of strings. The Wild card '*'
        may be used in the form of 'audio/*'. Wildcard MIME types are consulted
        only as a last resort when looking for an appropriate thumbnailer.
        
        @return: list of strings
        """
    
        return []


    def make_quick_thumbnail(self, f):
        """
        Returns a quick thumbnail for the given file. Quick thumbnails must
        be available immediately without having to create them first.
        May return an empty string.
        
        @param f: file object
        @return: path of thumbnail file
        """
        
        return ""
        
        
    def make_thumbnail(self, f, cb, *args):
        """
        Asynchronous callback for creating a thumbnail in the background.
        The callback must the called eventually, and may be called with an
        empty string if no thumbnail could be created.
        
        @param f: file object
        @param cb: callback handler with signature cb(thumbnail_path, *args)
        @param args: variable list of user arguments to the callback handler
        """
        
        cb("", *args)

