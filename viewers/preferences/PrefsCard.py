import theme

import gtk
import pango


class PrefsCard(gtk.VBox):

    def __init__(self, title):
    
        gtk.VBox.__init__(self)
        
        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.set_size_request(-1, 32)
        vp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#a0a0f0"))
        vp.show()
        self.pack_start(vp, False, False)
        
        lbl_title = gtk.Label(" " + title)
        lbl_title.modify_font(theme.font_headline)
        lbl_title.set_alignment(0.0, 0.5)
        lbl_title.show()
        vp.add(lbl_title)
        #self.pack_start(lbl_title, False, False)
        
