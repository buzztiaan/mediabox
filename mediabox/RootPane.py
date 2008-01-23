from ui.Widget import Widget
from ui.Pixmap import Pixmap
import theme

import threading
import gtk
import gobject


class RootPane(Widget):

    def __init__(self, esens):
    
        self.__buffer = Pixmap(None, 800, 480)
    
        Widget.__init__(self, esens)
        self.set_size(800, 480)


    def render_buffered(self):
    
        self.render_at(self.__buffer)
        self.get_screen().copy_pixmap(self.__buffer, 0, 0, 0, 0, 800, 480)
        
        
   
    def fx_fade_in(self, wait = True):
    
        STEP = 32
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        dst_pbuf = screen.render_on_pixbuf()
        pbuf = buf.render_on_pixbuf()
        finished = threading.Event()
        
        def f(i, pbuf, dst_pbuf):
            i = min(255, i)
            pbuf.composite(dst_pbuf, 0, 0, w, h, 0, 0, 1, 1,
                           gtk.gdk.INTERP_NEAREST, i)
            screen.draw_subpixbuf(dst_pbuf, 0, 0, 0, 0, w, h)
            if (i < 255):
                gobject.timeout_add(50, f, i + STEP, pbuf, dst_pbuf)
            else:
                finished.set()
                del pbuf
                del dst_pbuf
                
        f(32, pbuf, dst_pbuf)
        while (wait and not finished.isSet()): gtk.main_iteration()
