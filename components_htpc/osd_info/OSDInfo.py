from OSDComponent import OSDComponent
from com import msgs
from ui import pixbuftools
from ui.Pixmap import text_extents
from theme import theme
from mediabox import thumbnail

import gtk
import gobject
import pango


_OSD_FONT = pango.FontDescription("Nokia Sans Cn bold 28")


class OSDInfo(OSDComponent):

    def __init__(self):
    
        self.__file = None
    
        self.__frame = pixbuftools.make_frame(theme.mb_selection_frame,
                                              gtk.gdk.screen_width(), 80,
                                              True,
                                          pixbuftools.TOP | pixbuftools.BOTTOM)
    
        OSDComponent.__init__(self)

        self.set_size(gtk.gdk.screen_width(), 120)
        self.set_pos(0, 20) #gtk.gdk.screen_height() - 48 - 120)



    def render_this(self):

        tn = self.call_service(msgs.MEDIASCANNER_SVC_LOOKUP_THUMBNAIL, self.__file)
        
        screen = self.get_screen()
        screen.clear_translucent()
        screen.draw_pixbuf(self.__frame, 0, 30)
        
        if (tn):
            thumbnail.render_on_canvas(screen, 48, 0, 160, 120,
                                        tn, self.__file.mimetype)
                    
        tw, th = text_extents(self.__file.name, _OSD_FONT)
        screen.draw_text(self.__file.name, _OSD_FONT,
                         260, 30 + (80 - th) / 2,
                         "#ffffff")


    
    def handle_MEDIA_EV_LOADED(self, viewer, f):

        self.__file = f
        self.set_visible(True)
        self.render()
        #gobject.timeout_add(5000, self.set_visible, False)


    def handle_MEDIA_EV_PAUSE(self):
    
        if (self.__file):
            self.set_visible(True)
            self.render()
            

    def handle_MEDIA_EV_PLAY(self):

        gobject.timeout_add(5000, self.set_visible, False)

