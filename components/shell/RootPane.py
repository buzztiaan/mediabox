from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP, text_extents
from utils import logging
from theme import theme

import gtk
import gobject
import time


class RootPane(Widget):

    def __init__(self):
    
        self.__buffer = None
        self.__has_overlay = False
        
        Widget.__init__(self)
        self.set_size(100, 100)


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__buffer = Pixmap(None, w, h)
        self.__buffer.fill_area(0, 0, w, h, "#000000")


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
        logging.debug("rendering took %fs", (time.time() - now))


    def show_overlay(self, text, subtext, icon):
    
        w, h = self.get_size()
        screen = self.get_screen()
        TEMPORARY_PIXMAP.fill_area(0, 0, w, h, "#000000")

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
            
        gtk.gdk.window_process_all_updates()
        self.__has_overlay = True


    def hide_overlay(self):
    
        if (self.__has_overlay):
            self.__has_overlay = False
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            screen = self.get_screen()
        
            screen.draw_pixmap(self.__buffer, x, y)
            self.set_frozen(False)


    def fx_slide_in(self, wait = True):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        self.render_at(buf)

        
        def fx(params):
            from_y, to_y = params
            dy = (to_y - from_y) / 3
            if (dy > 0):
                screen.move_area(x, y, w, from_y, 0, dy)
                screen.copy_pixmap(buf, x, y + h - from_y - dy, 0, 0, w, dy)

                params[0] = from_y + dy
                params[1] = to_y
                return True
            else:
                dy = to_y - from_y
                screen.move_area(x, y, w, from_y, 0, dy)
                screen.copy_pixmap(buf, x, y + h - from_y - dy, 0, 0, w, dy)
                return False
        
        self.animate(50, fx, [0, h])

