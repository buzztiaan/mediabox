from utils.Observable import Observable
from ui.Widget import Widget
from ui.EventBox import EventBox
from ui.Pixmap import TEMPORARY_PIXMAP

import theme
import gtk
import gobject
import threading


class OverlayControls(Widget, Observable):

    OBS_PREVIOUS = 0
    OBS_NEXT = 1
    

    def __init__(self):

        self.__pos = 0
        self.__visible = True
    
        Widget.__init__(self)
        self.set_size(800, 480)
        ebox = EventBox()
        ebox.set_geometry(730, 0, 70, 480)
        self.add(ebox)
        ebox.connect(self.EVENT_BUTTON_RELEASE, self.__on_click)


    def __on_click(self, px, py):
    
        if (py < 80):
            self.update_observer(self.OBS_PREVIOUS)
        elif (py > 400):
            self.update_observer(self.OBS_NEXT)


    def set_visible(self, value):
    
        Widget.set_visible(self, value)
        self.__visible = value
        
        if (value):
            gobject.timeout_add(1500, self.fx_fade_out)


    def render_this(self):
    
        if (self.__visible):
            parent = self.get_parent()
            x, y = parent.get_screen_pos()
            w, h = parent.get_size()
            screen = self.get_screen()

            iw = theme.btn_previous_1.get_width()
            ih = theme.btn_previous_1.get_height()
            screen.draw_pixbuf(theme.btn_previous_2,
                               x + w - 70 + (70 - iw) / 2, y + 20)
            screen.draw_pixbuf(theme.btn_next_2,
                               x + w - 70 + (70 - iw) / 2, y + h - 20 - ih)
                           


    def fx_fade_out(self, wait = True):

        if (not self.is_visible()): return

        self.__visible = False
        return

        STEP = 32
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()        
        parent = self.get_parent()
        
        dst_pbuf = screen.render_on_pixbuf()
        self.__visible = False
        parent.render_at(TEMPORARY_PIXMAP, x, y)
        pbuf = TEMPORARY_PIXMAP.render_on_pixbuf()

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

