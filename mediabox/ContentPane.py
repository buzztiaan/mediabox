from ui.Widget import Widget
from ui.Pixmap import Pixmap
import theme

import gtk
import gobject
import threading


class ContentPane(Widget):

    def __init__(self, esens):
    
        Widget.__init__(self, esens)
        self.set_size(800, 400)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_subpixbuf(theme.background, 0, 0, x, y, w, h)


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


    def fx_raise(self, buf, wait = True):
    
        STEP = 20
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        finished = threading.Event()
        
        def fx(i):
            screen.move_area(x, y, w, h - i, 0, -STEP)
            screen.copy_pixmap(buf, 0, 0, x, y + h - i, w, i)
            if (i < 400):
                gobject.timeout_add(7, fx, i + STEP)
            else:
                finished.set()

        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration()
