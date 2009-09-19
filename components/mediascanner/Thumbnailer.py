from com import Component, msgs
from mediabox import config
from io import Downloader
from utils import logging

import os
import shutil
import gtk

# these modules handle the particular media types
import video
import audio
import image


class Thumbnailer(Component):
    """
    Component for creating and looking up thumbnail previews.
    """

    def __init__(self):
    
        self.__thumb_folder = os.path.abspath(config.thumbdir())
        self.__store_thumbnails_on_medium = config.store_thumbnails_on_medium()

        Component.__init__(self)

        # create directory for thumbnails if it doesn't exist yet
        try:
            if (not os.path.exists(self.__thumb_folder)):
                os.makedirs(self.__thumb_folder)
        except:
            pass


    def handle_MEDIASCANNER_SVC_LOOKUP_THUMBNAIL(self, f):

        if (self.has_thumbnail(f)):
            return self.get_thumbnail_path(f)
        else:
            return ""


    def handle_MEDIASCANNER_SVC_LOAD_THUMBNAIL(self, f, cb, *cb_args):

        self.__load_thumbnail(f, cb, *cb_args)
        return 0


    def handle_MEDIASCANNER_SVC_COPY_THUMBNAIL(self, f1, f2):

        self.__copy_thumbnail(f1, f2)
        return 0


    def handle_MEDIASCANNER_SVC_SET_THUMBNAIL(self, f, pbuf):

        thumbpath = self.__thumbnailer.get_thumbnail_path(f)
        pbuf.save(thumbpath, "jpeg")
        print "saving thumbnail for %s as %s" % (f.name, thumbpath)
        return thumbpath
        
        
        
    def __load_thumbnail(self, f, cb, *args):
    
        thumbnail_path = self.get_thumbnail_path(f)
        logging.debug("loading thumbnail for %s", f.full_path)
        
        if (f.thumbnail):
            self.__load_from_uri(f.thumbnail, thumbnail_path, cb, *args)
            
        else:
            self.__load_from_media(f, thumbnail_path, cb, *args)



    def __load_from_image(self, data, thumbnail_path):
                
        def on_size_available(loader, width, height):
            if (width > 160 or height > 120):
                factor = 1            
                factor1 = 160 / float(width)
                factor2 = 120 / float(height)
                factor = min(factor1, factor2)
                loader.set_size(int(width * factor), int(height * factor))
            #end if                

        try:
            loader = gtk.gdk.PixbufLoader()
            loader.connect("size-prepared", on_size_available)
            loader.write(data)
            loader.close()                                
            pbuf = loader.get_pixbuf()
        except:
            return

        pbuf.save(thumbnail_path, "jpeg")
        del pbuf
        del loader
        

        
    def __load_from_uri(self, uri, thumbnail_path, cb, *args):

        def on_download(d, a, t, data):
        
            if (d):
                # still loading
                data[0] += d
                
            elif (a == t):
                # aborted or finished
                self.__load_from_image(data[0], thumbnail_path)
                cb(thumbnail_path, *args)


        if (uri.startswith("/")):
            # it's a local file
            data = open(uri, "r").read()
            self.__load_from_image(data, thumbnail_path)
            cb(thumbnail_path, *args)

        else:
            Downloader(uri, on_download, [""])



    def __load_from_media(self, f, thumbnail_path, cb, *args):
    
        def on_generated():
            # no thumbnail generated? remember this
            #if (not os.path.exists(thumbnail_path)):
            #    self.mark_as_unavailable(f)
            #else:
            #    self.unmark_as_unavailable(f)
            
            cb(thumbnail_path, *args)
            
    
        for mod in (audio, video, image):
            if (mod.is_media(f)):
                mod.make_thumbnail_async(f, thumbnail_path, on_generated)
                return
        #end for
        
        cb(thumbnail_path, *args)


    def __copy_thumbnail(self, file1, file2):
        """
        Copies the thumbnail for C{file1} to be used for C{file2}.
        Does nothing if C{file1} has no thumbnail.
        """
        
        tn1 = self.get_thumbnail_path(file1)
        tn2 = self.get_thumbnail_path(file2)

        if (os.path.exists(tn1)):
            try:
                shutil.copyfile(tn1, tn2)
            except:
                pass

        

        
    def is_thumbnail_up_to_date(self, f):
        """
        Returns whether the thumbnail for the given file is up to date.
        Returns False if the thumbnail does not exist.
        """
                
        thumb = self.get_thumbnail_path(f)
        broken = thumb + ".broken"
        tn_epoch = config.thumbnails_epoch()
                
        if (os.path.exists(broken)):
            thumburi = broken
        else:
            thumburi = thumb

        try:
            mtime1 = f.mtime
            mtime2 = os.path.getmtime(thumburi)

            return (mtime1 <= mtime2 and mtime2 >= tn_epoch)

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
        return os.path.exists(thumb) and self.is_thumbnail_up_to_date(f)
        

        
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

