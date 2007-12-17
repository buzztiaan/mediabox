import config
import theme

import gtk
import gobject
import md5
import os
from utils import urlquote



class Thumbnailer(gtk.Window):
    """
    Widget for thumbnailing media items.
    """

    def __init__(self, parent = None):
                    
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.set_size_request(800, 400)
        if (parent and parent.window):
            parx, pary = parent.window.get_position()
            self.move(parx + 0, pary + 0)
        else:
            self.move(0, 0)
        
        fixed = gtk.Fixed()
        fixed.show()
        self.add(fixed)
                
        #lbl = gtk.Label("Looking For New Media Files...")
        #lbl.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))        
        #lbl.modify_font(theme.font_headline)
        #lbl.show()
        #fixed.put(lbl, 20, 10)
        
        # title
        self.__title = gtk.Label("")
        self.__title.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))        
        self.__title.modify_font(theme.font_plain)
        self.__title.set_size_request(800, -1)
        self.__title.set_alignment(0.5, 0.5)
        self.__title.show()
        fixed.put(self.__title, 0, 300)
        
        # progress label
        self.__progress_label = gtk.Label("")
        self.__progress_label.modify_font(theme.font_tiny)
        self.__progress_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))
        self.__progress_label.set_size_request(200, -1)
        self.__progress_label.set_alignment(1.0, 0.0)
        self.__progress_label.show()
        fixed.put(self.__progress_label, 580, 10)
                
        # thumbnail
        box = gtk.HBox()
        box.set_size_request(160, 120)
        box.show()
        fixed.put(box, 320, 140)

        self.__thumbnail = gtk.Image()
        self.__thumbnail.show()
        box.add(self.__thumbnail)

        # create directory for thumbnails if it doesn't exist yet
        try:
            if (not os.path.exists(config.thumbdir())):
                os.mkdir(config.thumbdir())
        except:
            pass


    def __get_md5sum(self, path):
    
        m = md5.new(path)
        return m.hexdigest()                        

    
    def set_thumbnail_for_uri(self, uri, tn):
        
        thumbpath = self.get_thumbnail(uri)
        
        self.__title.set_text(os.path.basename(uri))        
        try:
            pbuf = self.__load_image(tn)            
            self.__thumbnail.set_from_pixbuf(pbuf)
            pbuf.save(thumbpath, "jpeg")
            del pbuf
        except:
            pass

        while (gtk.events_pending()): gtk.main_iteration()

            
            
    def load_thumbnail(self, item):
    
        uri = item.get_uri()
        thumb = self.get_thumbnail(uri)
        item.set_thumbnail(thumb)
        
        
        
    def has_thumbnail(self, uri):
    
        thumb = self.get_thumbnail(uri)
        exists = os.path.exists(thumb)

        if (exists and os.path.exists(uri)):
            if (os.path.getmtime(uri) > os.path.getmtime(thumb)):
                exists = False
    
        if (not exists and self.__try_to_use_existing_thumb(uri)):
            exists = True    

        #if (not exists): print "NOT EXISTS", uri    
        return exists
       
       
       
    def get_thumbnail(self, uri):

        md5sum = self.__get_md5sum(uri)
        tn = os.path.join(config.thumbdir(), md5sum + ".jpg")

        return tn    


    def set_progress(self, n, total):
    
        self.__progress_label.set_text("%d of %d" % (n, total))



    def __load_image(self, uri):
    
        def on_size_available(loader, width, height):
            factor = 1
            factor1 = 160 / float(width)
            factor2 = 120 / float(height)
            factor = min(factor1, factor2)
            loader.set_size(int(width * factor), int(height * factor))
    
        loader = gtk.gdk.PixbufLoader()
        loader.connect("size-prepared", on_size_available)
        fd = open(uri, "r")
        while (True):
            data = fd.read(50000)            
            if (data):
                loader.write(data)
                while (gtk.events_pending()): gtk.main_iteration()
            else:
                break            
        #end while
        fd.close()
        try:
            loader.close()
            pbuf = loader.get_pixbuf()
            del loader
            return pbuf
        except:
            return None
        #del loader
        
        #return pbuf
        


    def __try_to_use_existing_thumb(self, uri):
        """
        Uses the thumbnail from another app, if available.
        """

        basename = os.path.basename(uri)
        thumbs = []

        # try osso
        name = self.__get_md5sum("file://" + urlquote.quote(uri)) + ".png"
        thumb_dir = os.path.expanduser("~/.thumbnails/osso")
        thumbs.append(os.path.join(thumb_dir, name))
        
        # try UKMP
        name = basename + "_thumb.jpg"
        vid_name = basename + ".jpg"
        thumb_dir = "/media/mmc1/covers"
        thumbs.append(os.path.join(thumb_dir, name))
        thumbs.append(os.path.join(thumb_dir, vid_name))
        
        
        for f in thumbs:
            if (os.path.exists(f)):
                print "found", f, "for", basename
                self.set_thumbnail_for_uri(uri, f)
                return True
        #end for
        
        return False
        
