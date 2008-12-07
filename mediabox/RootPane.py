from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP, text_extents
import theme

import threading
import gtk
import gobject


class RootPane(Widget):

    def __init__(self):
    
        self.__buffer = None
        self.__has_overlay = False
        
        Widget.__init__(self)
        self.set_size(100, 100)


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__buffer = Pixmap(None, w, h)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        

    def render_buffered(self):
    
        import time
        now = time.time()
        w, h = self.get_size()
        self.render_at(self.__buffer)
        self.get_screen().copy_pixmap(self.__buffer, 0, 0, 0, 0, w, h)
        print "rendering took %fs" % (time.time() - now)


    def show_overlay(self, text, subtext, icon):
    
        w, h = self.get_size()
        screen = self.get_screen()

        if (not self.__has_overlay):
            self.__buffer.draw_pixmap(screen, 0, 0)
        
        TEMPORARY_PIXMAP.draw_pixmap(self.__buffer, 0, 0)
        
        self.set_frozen(True)
        TEMPORARY_PIXMAP.fill_area(0, 0, w, h, theme.color_mb_overlay)

        tw, th = text_extents(text, theme.font_mb_overlay_text)
        tw2, th2 = text_extents(subtext, theme.font_mb_overlay_subtext)
       
        tx1 = (w - tw) / 2
        tx2 = (w - tw2) / 2
        ty = (h - th - th2) / 2
        
        TEMPORARY_PIXMAP.draw_text(text, theme.font_mb_overlay_text,
                                   tx1, ty,
                                   theme.color_mb_overlay_text)
        TEMPORARY_PIXMAP.draw_text(subtext, theme.font_mb_overlay_subtext,
                                   tx2, ty + th,
                                   theme.color_mb_overlay_subtext)
        

        if (icon):
            iw = icon.get_width()
            ih = icon.get_height()       
            TEMPORARY_PIXMAP.draw_pixbuf(icon, w - iw - 10, h - ih - 10)

        screen.draw_pixmap(TEMPORARY_PIXMAP, 0, 0)
            
        cnt = 0
        while (gtk.events_pending() and cnt < 10):
            gtk.main_iteration(False)
            cnt += 1

        self.__has_overlay = True


    def hide_overlay(self):
    
        self.__has_overlay = False
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_pixmap(self.__buffer, x, y)
        self.set_frozen(False)


    def fx_slide_in(self, wait = True):
    
        if (self.have_animation_lock()): return
        self.set_animation_lock(True)
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        self.set_frozen(False)
        self.render_at(buf)
        self.set_frozen(True)
        finished = threading.Event()
        
        def fx(from_y, to_y):
            dy = (to_y - from_y) / 10
            if (dy > 0):
                screen.move_area(x, y, w, from_y, 0, dy)
                screen.copy_pixmap(buf, x, y + h - from_y - dy, 0, 0, w, dy)
                gobject.timeout_add(10, fx, from_y + dy, to_y)
            else:
                dy = to_y - from_y
                screen.move_area(x, y, w, from_y, 0, dy)
                screen.copy_pixmap(buf, x, y + h - from_y - dy, 0, 0, w, dy)
                finished.set()
        
        self.set_events_blocked(True)
        fx(0, h)
        while (wait and not finished.isSet()): gtk.main_iteration(False)
        self.set_events_blocked(False)
        self.set_frozen(False)
        self.set_animation_lock(False)

