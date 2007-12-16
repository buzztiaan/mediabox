import theme
import gtk


_COVER_SIZE = 304

class TrackInfo(gtk.HBox):

    def __init__(self):
    
        gtk.HBox.__init__(self, spacing = 48)
        self.set_border_width(48)
    
        self.__cover = gtk.Image()
        self.__cover.set_alignment(0.5, 0.0)
        self.__cover.show()
        self.pack_start(self.__cover, False, False, 0)
        
        vbox = gtk.VBox()
        vbox.show()
        self.pack_start(vbox, True, True, 0)
        
        self.__title = gtk.Label("")
        self.__title.set_alignment(0.0, 0.0)
        self.__title.modify_font(theme.font_headline)
        self.__title.show()
        vbox.pack_start(self.__title, False, False)

        self.__info = gtk.Label("")
        self.__info.set_alignment(0.0, 0.0)
        self.__info.modify_font(theme.font_plain)
        self.__info.show()
        vbox.pack_start(self.__info, False, False, 24)
                


    def set_cover(self, cover):

        try:
            pbuf = gtk.gdk.pixbuf_new_from_file(cover)    
        except:
            pbuf = theme.viewer_music_unknown
            
        scaled = pbuf.scale_simple(_COVER_SIZE, _COVER_SIZE, gtk.gdk.INTERP_BILINEAR)
        self.__cover.set_from_pixbuf(scaled)
        
        del pbuf
        del scaled
        
        
    def set_title(self, title):
    
        self.__title.set_text(title)
        
        
    def set_info(self, album, artist):
    
        self.__info.set_markup("<b>Album:</b>\t%s\n"
                               "<b>Artist:</b>\t%s" \
                               % (album or "-", artist or "-"))
                             
