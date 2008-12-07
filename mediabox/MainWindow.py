from ui.EventSensor import EventSensor
from utils import maemo
import config

import gtk
import gobject
if (maemo.IS_MAEMO): import hildon


_Window = maemo.IS_MAEMO and hildon.Window or gtk.Window


class MainWindow(_Window, EventSensor):

    def __init__(self):
    
        if (maemo.IS_MAEMO):
            _Window.__init__(self)
            self.fullscreen()
            self.set_size_request(800, 480)
            self.set_resizable(False)
        else:
            _Window.__init__(self, gtk.WINDOW_TOPLEVEL)
            #self.set_decorated(False)
            if (gtk.gdk.screen_width() == 800):
                self.fullscreen()
            else:
                #self.set_default_size(800, 480)
                self.set_size_request(800, 480)
                #self.fullscreen()

        self._fixed = gtk.Fixed()
        self._fixed.show()
        self.add(self._fixed)

        EventSensor.__init__(self, self)
        
        
        #def f():
        #    pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 8, 8)
        #    pbuf.fill(0x00000000)
        #    csr = gtk.gdk.Cursor(gtk.gdk.display_get_default(), pbuf, 0, 0)
        #    self.window.set_cursor(csr)
        #gobject.idle_add(f)


    def put(self, child, x, y):
    
        self._fixed.put(child, x, y)
        
        
    def move(self, child, x, y):
    
        self._fixed.move(child, x, y)

