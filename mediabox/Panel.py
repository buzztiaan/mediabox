from utils.Observable import Observable
from ui.ImageButton import ImageButton
import theme

import gtk


class Panel(gtk.Fixed, Observable):

    OBS_NEXT_PANEL = 0
    

    def __init__(self, with_next_button = True):
    
        self.__has_next_button = with_next_button
    
        gtk.Fixed.__init__(self)
        self.set_app_paintable(True)        
        self.set_size_request(800, 80)
        
        self.__bg = gtk.Image()
        self.__bg.set_from_pixbuf(theme.panel)
        self.__bg.show()
        self.put(self.__bg, 0, 0)
        
        self.box = gtk.HBox()
        self.box.set_size_request(784, 80)
        self.box.show()
        self.put(self.box, 8, 0)

        if (with_next_button):
            btn = self._create_button(theme.btn_turn_1, theme.btn_turn_2,
                                      lambda x,y:self._next_panel())
            btn.show()
        
            spacing = gtk.HBox()
            spacing.show()
            self.box.pack_start(spacing, True, True)
        #end if


    def _create_button(self, img1, img2, cb):
    
        btn = ImageButton(img1, img2, theme.panel_button_bg)
        btn.set_size_request(80, -1)
        btn.connect("button-release-event", cb)
        self.box.pack_start(btn, False, False)
        
        return btn    


    def has_next_button(self):
    
        return self.__has_next_button
        
        
    def _next_panel(self):
    
        self.update_observer(self.OBS_NEXT_PANEL)
