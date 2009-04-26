from com import Component
from ui.HilightingWidget import HilightingWidget
from ui.Pixmap import Pixmap

import gtk
import gobject


class OSDComponent(Component, HilightingWidget):

    def __init__(self):
    
        Component.__init__(self)
        HilightingWidget.__init__(self)
        
        self.__window = gtk.Window(gtk.WINDOW_POPUP)
        #self.__window.set_size_request(gtk.gdk.screen_width(), gtk.gdk.screen_height())
        self.__window.set_app_paintable(True)
        
        self.__window.set_events(gtk.gdk.EXPOSURE_MASK)
        self.__window.connect("expose-event", self.__on_expose)

        # switch on compositing
        scr = self.__window.get_screen()
        cmap = scr.get_rgba_colormap() or scr.get_rgb_colormap()
        self.__window.set_colormap(cmap)

        self.set_window(self.__window)


    def __on_expose(self, src, ev):
    
        if (not self.get_screen()):
            screen = Pixmap(self.__window.window)
            self.set_screen(screen)
            screen.clear_translucent()
               
        x, y, w, h = ev.area

        screen = self.get_screen()
        if (screen):
            screen.restore(x, y, w, h)
            

    def set_size(self, w, h):
    
        w = int(w)
        h = int(h)
        HilightingWidget.set_size(self, w, h)
        #self.__window.set_size_request(w, h)
        self.__window.resize(w, h)
        
        
        
    def set_pos(self, x, y):
    
        self.__window.move(x, y)
        
        
    def set_visible(self, value):
    
        if (value):
            self.__window.show()
        else:
            self.__window.hide()

        while (not self.get_screen()):
            gtk.main_iteration(False)

        HilightingWidget.set_visible(self, value)

