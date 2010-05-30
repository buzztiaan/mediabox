from Component import Component
from mediabox import config
from ui import pixbuftools
from utils import logging
import msgs

import os
import gtk


# do not use any thumbnails from before this date
_TN_EPOCH = 1275153936

# static pixbuf for scaling down
_PBUF = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 120, 120)


class Thumbnailer(Component):
    """
    Base class for Thumbnailer components. Thumbnailers handle creating
    thumbnails of files.
    @since: 2009.10
    """

    __THUMB_FOLDER = os.path.abspath(config.thumbdir())
    __STORE_ON_MEDIUM = config.store_thumbnails_on_medium()


    def __init__(self):
    
        Component.__init__(self)
 
        # create directory for thumbnails if it doesn't exist yet
        try:
            if (not os.path.exists(self.__THUMB_FOLDER)):
                os.makedirs(self.__THUMB_FOLDER)
        except:
            pass
        
        
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
        @return: tuple of thumbnail file and whether the thumbnail is final
        """
        
        return ("", True)
        
        
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



    def _set_thumbnail(self, f, pbuf):
        """
        Saves the given pixbuf as thumbnail for the given file.
        Thumbnailers may use this method for caching thumbnails.
        """
    
        # always scale down large thumbnails
        if (pbuf.get_width() > 160 or pbuf.get_height() > 160):
            _PBUF.fill(0x00000000)
            pixbuftools.fit_pbuf(_PBUF, pbuf, 0, 0, 120, 120)
            pbuf = _PBUF
        #end if
    
        path = self.__get_thumbnail_path(f)
        try:
            pbuf.save(path, "jpeg")
            return path
        except:
            logging.error("cannot save thumbnail:\n%s", logging.stacktrace())
            return ""
        
        
    def _get_thumbnail(self, f):
        """
        Returns the path of a cached thumbnail for the given file. Returns
        an empty string if no thumbnail was found.
        Thumbnailers may use this method for caching thumbnails.
        """
    
        path = self.__get_thumbnail_path(f)
        if (os.path.exists(path)):
            mtime1 = f.mtime
            mtime2 = os.path.getmtime(path)
            tn_epoch = max(_TN_EPOCH, config.thumbnails_epoch())
            if (mtime1 <= mtime2 and mtime2 >= tn_epoch):
                return path
            else:
                return ""
        else:
            return ""

        
    
    def __get_thumbnail_path(self, f):
        """
        Returns the full path for the thumbnail for the given file.
        """

        md5 = f.thumbnail_md5
        thumb_fallback = os.path.join(self.__THUMB_FOLDER,
                                      md5 + ".jpg")
        if (not self.__STORE_ON_MEDIUM):
            return thumb_fallback

        else:
            medium = f.medium
            if (not medium or medium == "/"):
                return thumb_fallback

            else:
                prefix = os.path.join(medium, ".mediabox", "thumbnails")
                if (not os.path.exists(prefix)):
                    try:
                        os.makedirs(prefix)
                    except:
                        logging.error("could not create thumbnails directory:"
                                      "%s\n%s", prefix, logging.stacktrace())
                        return thumb_fallback
                #end if
            #end if
            
            thumb = os.path.join(prefix, md5 + ".jpg")
            return thumb

