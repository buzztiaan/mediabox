import ui
from ui.Widget import Widget
from utils import maemo
import config

import gtk
import gobject
if (maemo.IS_MAEMO): import hildon


_Window = maemo.IS_MAEMO and hildon.Window or gtk.Window


class MainWindow(_Window):

    def __init__(self):
    
        self.__widget = None
        
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
                self.set_default_size(800, 480)
                #self.set_size_request(480, 800)
                #self.fullscreen()

        # try to switch on compositing
        ui.try_rgba(self)

        self._fixed = gtk.Fixed()
        self._fixed.show()
        self.add(self._fixed)

       
        self.connect("button-press-event", self.__on_button_pressed)
        self.connect("button-release-event", self.__on_button_released)
        self.connect("motion-notify-event", self.__on_motion)
        
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)
        
        
        #def f():
        #    pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 8, 8)
        #    pbuf.fill(0x00000000)
        #    csr = gtk.gdk.Cursor(gtk.gdk.display_get_default(), pbuf, 0, 0)
        #    self.window.set_cursor(csr)
        #gobject.idle_add(f)


    def set_widget_for_events(self, w):
    
        self.__widget = w


    def __on_button_pressed(self, src, ev):

        px, py = src.get_pointer()
        self.__widget._handle_event(Widget.EVENT_BUTTON_PRESS, px, py)

        
    def __on_button_released(self, src, ev):

        px, py = src.get_pointer()
        self.__widget._handle_event(Widget.EVENT_BUTTON_RELEASE, px, py)
        
        
    def __on_motion(self, src, ev):

        px, py = src.get_pointer()
        self.__widget._handle_event(Widget.EVENT_MOTION, px, py)


    def put(self, child, x, y):
    
        self._fixed.put(child, x, y)
        
        
    def move(self, child, x, y):
    
        self._fixed.move(child, x, y)

