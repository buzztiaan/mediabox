from mediabox import config
from utils import logging
import os


class Thumbnailer(object):
    """
    Class for retrieving thumbnails.
    """

    def __init__(self):
    
        self.__thumb_folder = ""
        self.__store_thumbnails_on_medium = config.store_thumbnails_on_medium()



    def get_thumb_folder(self):
        """
        Returns the path of the thumbnail folder.
        """
        
        return self.__thumb_folder
       

    def set_thumb_folder(self, path):
        """
        Sets the folder for storing the thumbnails.
        """
    
        self.__thumb_folder = path
        # create directory for thumbnails if it doesn't exist yet
        try:
            if (not os.path.exists(path)):
                os.makedirs(path)
        except:
            pass          

        
    def is_thumbnail_up_to_date(self, f):
        """
        Returns whether the thumbnail for the given file is up to date.
        Returns False if the thumbnail does not exist.
        """
                
        thumb = self.get_thumbnail_path(f)
        broken = thumb + ".broken"
                
        if (os.path.exists(broken)):
            thumburi = broken
        else:
            thumburi = thumb
          
        try:
            mtime1 = os.path.getmtime(f.resource)
            mtime2 = os.path.getmtime(thumburi)
            #f.mtime = mtime1

            return (mtime1 <= mtime2)

        except:
            return False        


    def mark_as_unavailable(self, f):
        """
        Marks the thumbnail for the given file as unavailable so that we
        don't try to thumbnail it again, unless the mtime has changed.
        """
        
        # simply touch it
        thumb = self.get_thumbnail_path(f) + ".broken"
        logging.debug("marking thumbnail for %s as broken: %s", f, thumb)
        try:
            open(thumb, "w")
        except:
            pass


    def unmark_as_unavailable(self, f):
        """
        Removes the thumbnail unavailability mark on the given file.
        """
        
        thumb = self.get_thumbnail_path(f) + ".broken"
        logging.debug("unmarking thumbnail for %s as broken: %s", f, thumb)
        try:
            os.unlink(thumb)
        except:
            pass        


    def remove_thumbnail(self, f):
        """
        Removes the thumbnail for the given file.
        """

        thumb = self.get_thumbnail_path(f)
        try:
            os.unlink(thumb)
        except:
            pass
        

    def has_thumbnail(self, f):
        """
        Returns whether a thumbnail exists for the given file.
        """

        thumb = self.get_thumbnail_path(f)
        return os.path.exists(thumb)
        

        
    def get_thumbnail_path(self, f):
        """
        Returns the path for the thumbnail for the given file.
        """

        thumb_fallback = os.path.join(self.__thumb_folder,
                                      f.thumbnail_md5 + ".jpg")
        if (not self.__store_thumbnails_on_medium):
            return thumb_fallback

        else:
            medium = f.medium
            if (not medium or medium == "/"):
                prefix = self.__thumb_folder
            else:
                prefix = os.path.join(medium, ".mediabox", "thumbnails")
                if (not os.path.exists(prefix)):
                    try:
                        os.makedirs(prefix)
                    except:
                        logging.error("could not create thumbnails directory:"
                                      "%s\n%s", prefix, logging.stacktrace())
                        prefix = self.__thumb_folder
            #end if
            thumb = os.path.join(prefix, f.thumbnail_md5 + ".jpg")
            return thumb

