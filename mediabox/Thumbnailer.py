import config
import theme

import gtk
import gobject
import md5
import os



class Thumbnailer(gtk.Window):
    """
    Widget for thumbnailing media items.
    """

    def __init__(self, parent = None):
                    
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#e0e0e0"))
        self.set_size_request(800, 200)
        if (parent and parent.window):
            parx, pary = parent.window.get_position()
            self.move(parx + 0, pary + 140)
        else:
            self.move(0, 140)
        
        fixed = gtk.Fixed()
        fixed.show()
        self.add(fixed)
                
        lbl = gtk.Label("Looking For New Media Files...")
        lbl.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))        
        lbl.modify_font(theme.font_headline)
        lbl.show()
        fixed.put(lbl, 20, 10)
        
        # title
        self.__title = gtk.Label("")
        self.__title.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))        
        self.__title.modify_font(theme.font_plain)
        self.__title.show()
        fixed.put(self.__title, 20, 170)
        
        # progress label
        self.__progress_label = gtk.Label("")
        self.__progress_label.modify_font(theme.font_tiny)
        self.__progress_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))
        self.__progress_label.set_size_request(200, -1)
        self.__progress_label.set_alignment(1.0, 0.0)
        self.__progress_label.show()
        fixed.put(self.__progress_label, 580, 10)
        
        # thumbnail
        self.__thumbnail = gtk.Image()
        self.__thumbnail.show()
        fixed.put(self.__thumbnail, 600, 40)                

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
        


    def set_thumbnail(self, item, tn):

        uri = item.get_uri()
        thumb = self.get_thumbnail(uri)

        self.__thumbnail.set_from_pixbuf(tn)
        self.__title.set_text(os.path.basename(uri))
        tn.save(thumb)
        
        while (gtk.events_pending()): gtk.main_iteration()                                            
        item.set_thumbnail(thumb)
            
            
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
        
