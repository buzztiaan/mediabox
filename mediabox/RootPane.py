from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
import theme

import threading
import gtk
import gobject


class RootPane(Widget):

    def __init__(self):
    
        self.__buffer = Pixmap(None, 800, 480)
    
        Widget.__init__(self)
        self.set_size(800, 480)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_bg)
        

    def render_buffered(self):
    
        self.render_at(self.__buffer)
        self.get_screen().copy_pixmap(self.__buffer, 0, 0, 0, 0, 800, 480)
        
        
   
    def fx_fade_in(self, wait = True):
    
        STEP = 16
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        pbuf1 = screen.render_on_pixbuf()
        self.render_at(TEMPORARY_PIXMAP)
        pbuf2 = TEMPORARY_PIXMAP.render_on_pixbuf()
        finished = threading.Event()

        for i in range(0, 255, STEP):
            pbuf2.composite(pbuf1, 0, 0, w, h, 0, 0, 1, 1,
                            gtk.gdk.INTERP_NEAREST, i)
            screen.draw_pixbuf(pbuf1, 0, 0)
            #del pbuf
            #if (i > 0):
            #    gobject.timeout_add(10, f, i - STEP)
            #else:
            #    finished.set()
        return

        def g(i):
            i = min(255, i)        
            pbuf = pbuf2.composite_color_simple(w, h, gtk.gdk.INTERP_NEAREST,
                                                i, 1024, 0, 0)
            screen.draw_pixbuf(pbuf, 0, 0)
            del pbuf
            if (i < 255):
                gobject.timeout_add(10, g, i + STEP)
            else:
                finished.set()
        
        f(255 - STEP)
        while (wait and not finished.isSet()): gtk.main_iteration()
        finished = threading.Event()
        g(STEP)
        while (wait and not finished.isSet()): gtk.main_iteration()
        return
        
        dst_pbuf = screen.render_on_pixbuf()
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        pbuf = buf.render_on_pixbuf()
        finished = threading.Event()
        
        def f(i, pbuf, dst_pbuf):
            i = min(255, i)
            pbuf.composite(dst_pbuf, 0, 0, w / 8, h / 8, 0, 0, 1, 1,
                           gtk.gdk.INTERP_NEAREST, i)
            screen.draw_subpixbuf(dst_pbuf, 0, 0, 0, 0, w, h)
            if (i < 255):
                gobject.timeout_add(50, f, i + STEP, pbuf, dst_pbuf)
            else:
                finished.set()
                del pbuf
                del dst_pbuf
                
        f(STEP, pbuf, dst_pbuf)
        while (wait and not finished.isSet()): gtk.main_iteration()

        
    def fx_fade_out(self, wait = True):
    
        STEP = 32
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        dst_pbuf = screen.render_on_pixbuf()
        buf = TEMPORARY_PIXMAP
        buf.fill_area(x, y, w, h, theme.color_bg)
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
                
        f(STEP, pbuf, dst_pbuf)
        while (wait and not finished.isSet()): gtk.main_iteration()


    def fx_slide_in(self, wait = True):
    
        STEP = 20
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        self.set_frozen(False)
        self.render_at(buf)
        self.set_frozen(True)
        finished = threading.Event()
        
        def fx(i):
            if (i > 0):
                screen.move_area(x, y, w, i, 0, STEP)
            screen.copy_pixmap(buf, x, y + h - i, 0, 0, w, STEP)
            if (i < 480):
                gobject.timeout_add(7, fx, i + STEP)
            else:
                finished.set()

        self.set_events_blocked(True)
        fx(STEP)
        while (wait and not finished.isSet()): gtk.main_iteration()
        self.set_events_blocked(False)

