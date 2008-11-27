from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
import theme

import threading
import gtk
import gobject


class RootPane(Widget):

    def __init__(self):
    
        self.__buffer = None
        
        Widget.__init__(self)
        self.set_size(100, 100)


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__buffer = Pixmap(None, w, h)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_bg)
        

    def render_buffered(self):
    
        import time
        now = time.time()
        w, h = self.get_size()
        self.render_at(self.__buffer)
        self.get_screen().copy_pixmap(self.__buffer, 0, 0, 0, 0, w, h)
        print "rendering took %fs" % (time.time() - now)
        
   

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
            if (i > STEP):
                screen.move_area(x, y, w, i - STEP, 0, STEP)
            screen.copy_pixmap(buf, x, y + h - i, 0, 0, w, STEP)
            if (i < h):
                gobject.timeout_add(7, fx, i + STEP)
            else:
                finished.set()

        self.set_events_blocked(True)
        fx(STEP)
        while (wait and not finished.isSet()): gtk.main_iteration(False)
        self.set_events_blocked(False)
        self.set_frozen(False)
