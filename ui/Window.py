from Widget import Widget
from ui import try_rgba
from Pixmap import Pixmap
from Widget import Widget
from utils import maemo

import gtk


class Window(Widget):

    EVENT_CLOSED = "event-closed"
    

    def __init__(self, is_toplevel):
    
        self.__size = (0, 0)
        self.__fixed = None
    
        Widget.__init__(self)
    
        if (is_toplevel):
            if (maemo.IS_MAEMO):
                import hildon
                self.__window = hildon.Window()
                self.__window.fullscreen()
            else:
                self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            
            #self.set_size(800, 480)
            #self.__window.set_resizable(False)
        else:
            self.__window = gtk.Window(gtk.WINDOW_POPUP)


        self.__window.connect("configure-event", self.__on_configure)
        self.__window.connect("expose-event", self.__on_expose)
        self.__window.connect("button-press-event", self.__on_button_pressed)
        self.__window.connect("button-release-event", self.__on_button_released)
        self.__window.connect("motion-notify-event", self.__on_motion)
        self.__window.connect("key-press-event", self.__on_key_pressed)
        self.__window.connect("key-release-event", self.__on_key_released)
        self.__window.connect("delete-event", self.__on_close_window)

        
        self.__window.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                 gtk.gdk.BUTTON_RELEASE_MASK |
                                 gtk.gdk.POINTER_MOTION_MASK |
                                 gtk.gdk.POINTER_MOTION_HINT_MASK |
                                 gtk.gdk.KEY_PRESS_MASK |
                                 gtk.gdk.KEY_RELEASE_MASK)


        self.__window.set_size_request(800, 480)
        try_rgba(self.__window)
        self.__window.set_app_paintable(True)
        self.__window.realize()


        self.__fixed = gtk.Fixed()
        self.__fixed.show()
        self.__window.add(self.__fixed)
        self.__screen = None #Pixmap(self.__window.window)

                
        self.set_window(self)
        self.__check_window_size()


    def get_gtk_window(self):
    
        return self.__window


    def __check_window_size(self):

        if (self.__size != self.__window.get_size()):
            w, h = self.__window.get_size()
            self.__screen = Pixmap(self.__window.window)
            self.set_screen(self.__screen)
            self.__size = (w, h)
            
            Widget.set_size(self, w, h)
            for c in self.get_children():
                c.set_size(w, h)

            self.render()


    def __on_configure(self, src, ev):

        self.__check_window_size()


    def __on_expose(self, src, ev):
    
        x, y, w, h = ev.area
        self.__screen.restore(x, y, w, h)


    def __on_close_window(self, src, ev):
    
        self.send_event(self.EVENT_CLOSED)
        return True
        

    def __on_button_pressed(self, src, ev):

        px, py = src.get_pointer()
        self._handle_event(self.EVENT_BUTTON_PRESS, px, py)
        return True

        
    def __on_button_released(self, src, ev):

        px, py = src.get_pointer()
        self._handle_event(self.EVENT_BUTTON_RELEASE, px, py)
        return True
        
        
    def __on_motion(self, src, ev):

        px, py = src.get_pointer()
        self._handle_event(self.EVENT_MOTION, px, py)
        return True


    def __on_key_pressed(self, src, ev):
    
        keyval = ev.keyval
        c = gtk.gdk.keyval_to_unicode(keyval)
        if (c > 31):
            key = unichr(c)
        else:
            key = gtk.gdk.keyval_name(keyval)

        self.send_event(self.EVENT_KEY_PRESS, key)        
        
        # kill queued events
        if (key in ["Up", "Down", "Left", "Right"]):
            while (True):
                e = gtk.gdk.event_get()
                if (not e): break

        return True


    def __on_key_released(self, src, ev):

        keyval = ev.keyval
        c = gtk.gdk.keyval_to_unicode(keyval)
        if (c > 31):
            key = unichr(c)
        else:
            key = gtk.gdk.keyval_name(keyval)

        self.send_event(self.EVENT_KEY_RELEASE, key)
                
        return True


    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)


    def get_pos(self):
    
        return self.__window.window.get_position()
        
        
    def get_screen_pos(self):
    
        return (0, 0)


    def set_pos(self, x, y):
    
        Widget.set_pos(self, 0, 0)
        self.__window.move(x, y)
        
        
    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__window.set_size_request(w, h)


    def get_size(self):

        w, h = self.__window.get_size()
        return (w, h)


    def _visibility_changed(self):
    
        if (self.is_visible()):
            self.__window.show()
            self.render()
        else:
            self.__window.hide()



    def put(self, child, x, y):
    
        if (not self.__fixed):
            self.__fixed = gtk.Fixed()
            self.__fixed.show()
            self.__window.add(self.__fixed)
    
        self.__fixed.put(child, x, y)
        
        
    def move(self, child, x, y):
        assert self.__fixed
        
        self.__fixed.move(child, x, y)
        
        
    def present(self):
    
        self.__window.present()


    def iconify(self):
    
        self.__window.iconify()


    def set_title(self, title):
    
        self.__window.set_title(title)

