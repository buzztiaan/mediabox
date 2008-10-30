"""
Object representing a file or folder on a storage device.
"""

import md5


class File(object):

    FILE = "application/x-other"
    DIRECTORY = "application/x-folder"
    

    def __init__(self, device):
    
        self.__device = device


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

        self.parent = ""
        """name of parent folder, if any (can be used for grouping items)"""

        self.thumbnail = ""
        """may contain the URI of a thumbnail image"""
        
        self.mimetype = self.FILE
        """MIME type of the file"""
               
        self.resource = ""
        """URI for accessing the file"""

        
        #self.title = ""
        #self.artist = ""
        #self.album = ""
        #self.trackno = 0
        self.child_count = 0
        self.emblem = None
        
        self.tags = None




    def __cmp__(self, other):
    
        if (other):
            return cmp((self.name, self.resource), (other.name, other.resource))
        else:
            return 1


    def __repr__(self):
    
        return "<" + self.full_path + ">"


    def __get_full_path(self):
    
        return self.__device.get_prefix() + self.path
        
    full_path = property(__get_full_path)
    """full virtual path of the file"""
    
    
    def __get_source_icon(self):
    
        return self.__device.get_icon()
        
    source_icon = property(__get_source_icon)
    """pixbuf icon representing the source device"""


    def __get_md5(self):
        
        try:
            return self.__md5
        except:
            self.__md5 = md5.new(self.full_path).hexdigest()
            return self.__md5

    md5 = property(__get_md5)
    """MD5 sum for uniquely identifying the file internally"""

    

    def __get_thumbnail_md5(self):
    
        try:
            return self.__thumbnail_md5
        except:
            return self.md5
            
    def __set_thumbnail_md5(self, v):
    
        self.__thumbnail_md5 = v

    thumbnail_md5 = property(__get_thumbnail_md5,
                             __set_thumbnail_md5)
    """MD5 sum for uniquely identifying the file's thumbnail preview"""

       
        
    def new_file(self):
    
        return self.__device.new_file(self.path)
        
        
    def delete(self):
        """
        Deletes this file.
        """
    
        return self.__device.delete(self)
        
        
    def get_children(self):
        """
        Returns a list of children of this folder.
        """
    
        return self.__device.ls(self.path)


    def get_children_async(self, cb, *args):
        
        self.__device.ls_async(self.path, cb, *args)


    def load(self, maxlen, cb, *args):
        
        self.__device.load(self.get_resource(), maxlen, cb, *args)


    def get_fd(self):
    
        return self.__device.get_fd(self.resource)
        
        
    def get_resource(self):
    
        return self.__device.get_resource(self)
        
        
    def keep(self):
    
        self.__device.keep(self)

