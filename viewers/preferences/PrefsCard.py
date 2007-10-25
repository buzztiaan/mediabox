import gtk
import pango


class PrefsCard(gtk.VBox):

    def __init__(self, title):
    
        gtk.VBox.__init__(self)
        
        lbl_title = gtk.Label(title)
        lbl_title.modify_font(pango.FontDescription("Sans bold 24"))
        lbl_title.set_size_request(-1, 32)        
        lbl_title.show()
        self.pack_start(lbl_title, False, False)
        
