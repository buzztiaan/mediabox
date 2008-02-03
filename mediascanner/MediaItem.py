class MediaItem(object):
    """
    Class representing a media item. This is merely a struct.
    """
    __slots__ = ["mediatype", "name", "uri", "md5", "mtime", "scantime",
                 "thumbnail", "thumbnail_pmap"]
                 
    def __init__(self):
    
        self.mediatype = 0            # type of media
        self.name = ""                # readable name
        self.uri = ""                 # media URI
        self.md5 = ""                 # MD5 sum for identifying
        self.mtime = 0                # modification time
        self.scantime = 0             # scan time
        self.thumbnail = ""           # thumbnail path
        self.thumbnail_pmap = None    # actual thumbnail pixmap
        
    # TODO: get rid of
    def get_thumbnail(self): return self.thumbnail_pmap
    
