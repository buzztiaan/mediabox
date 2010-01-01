from Widget import Widget
from ui import try_rgba
from Pixmap import Pixmap
from Widget import Widget
from utils.MiniXML import MiniXML
import platforms
from theme import theme

import gtk
import os
try:
    import hildon
except:
    hildon = None


class Window(Widget):
    """
    Base class for windows.
    """

    TYPE_TOPLEVEL = 0
    TYPE_DIALOG = 1


    EVENT_CLOSED = "event-closed"
    

    def __init__(self, win_type):
        """
        Creates a new window.
        
        @param win_type: type of window
        """
    
        self.__type = win_type
        self.__size = (0, 0)
        self.__fixed = None
    
        Widget.__init__(self)
    
        if (self.__type == self.TYPE_TOPLEVEL):
            if (platforms.PLATFORM in (platforms.MAEMO5, platforms.MER)):
                self.__window = hildon.StackableWindow()

            elif (platforms.PLATFORM == platforms.MAEMO4):
                self.__window = hildon.Window()
                self.__window.fullscreen()
                
            else:
                self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
                self.__window.set_default_size(800, 480)
            
        elif (self.__type == self.TYPE_DIALOG):
            self.__window = gtk.Dialog()

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


        self.set_visible(False)
        try_rgba(self.__window)
        self.__window.set_app_paintable(True)
        self.__window.realize()

        if (platforms.PLATFORM == platforms.MAEMO5):
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)

        
        if (platforms.PLATFORM in (platforms.MAEMO5, platforms.MER)):
            # we need to notify Maemo5 that we want to use the volume keys
            self.__window.window.property_change("_HILDON_ZOOM_KEY_ATOM",
                                                 "XA_INTEGER", 32,
                                                 gtk.gdk.PROP_MODE_REPLACE,
                                                 [1])                
        

        self.__fixed = gtk.Fixed()
        self.__fixed.show()

        if (self.__type == self.TYPE_TOPLEVEL):
            self.__window.add(self.__fixed)
        else:
            self.__window.vbox.add(self.__fixed)
        
        self.__screen = None

        """
        # hide mouse cursor
        if (hide_cursor):
            pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 8, 8)
            pbuf.fill(0x00000000)
            csr = gtk.gdk.Cursor(gtk.gdk.display_get_default(), pbuf, 0, 0)
            self.__window.window.set_cursor(csr)
            del pbuf
        #end if
        """
                
        self.set_window(self)


    def get_gtk_window(self):
        """
        Returns the associated GtkWindow of this window.
        
        @return: GtkWindow object
        """
    
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
    
        if (self.__screen):
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

        self.send_event(self.EVENT_KEY_PRESSED, key)
        
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

        self.send_event(self.EVENT_KEY_RELEASED, key)
                
        return True


    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)


    def get_pos(self):
    
        return self.__window.window.get_position()
        
        
    def get_screen_pos(self):
    
        return (0, 0)


    def set_pos(self, x, y):
    
        Widget.set_pos(self, 0, 0)
        #self.__window.move(x, y)
        
        
    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        #self.__window.set_size_request(w, h)
        self.__window.resize(w, h)


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


    def set_fullscreen(self, v):
    
        if (v):
            self.__window.fullscreen()
        else:
            self.__window.unfullscreen()


    def set_title(self, title):
    
        self.__window.set_title(title)


    def __set_portrait_property(self, prop, value):

        self.__window.window.property_change(prop, "CARDINAL", 32,
                                             gtk.gdk.PROP_MODE_REPLACE,
                                             [value])
    
    
    def set_portrait_mode(self, v):
        """
        Switches between landscape and portrait mode on supported platforms.
        @since: 2009.09
        """
        
        if (platforms.PLATFORM == platforms.MAEMO5):
            if (v):
                self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
                self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST", 1)
            else:
                self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
                self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST", 0)

        elif (platforms.PLATFORM == platforms.MAEMO4):
            if (v):
                os.system("xrandr -o left")
            else:
                os.system("xrandr -o normal")

        #end if


    def set_busy(self, value):
        """
        Marks this window as busy. Depending on the platform this can e.g.
        change the mouse cursor or display a throbber animation in the title
        bar.
        @since: 2009.12.29
        
        @param value: whether this window is busy
        """
        
        if (hildon):
            hildon.hildon_gtk_window_set_progress_indicator(self.__window,
                                                            value and 1 or 0) 
        else:
            csr = gtk.gdk.Cursor(value and gtk.gdk.WATCH or gtk.gdk.LEFT_PTR)
            self.__window.window.set_cursor(csr)
        #end if


    def set_menu_xml(self, xml, bindings):
        """
        Sets the window menu from a XML description.
        @since 2009.11.19
        
        @param xml: XML description of the menu
        @param bindings: dictionary mapping XML node IDs to callback handlers
        """
    
        if (platforms.PLATFORM != platforms.MAEMO5): return

        dom = MiniXML(xml).get_dom()        
        menu = hildon.AppMenu()
        
        for node in dom.get_children():
            name = node.get_name()
            if (name == "item"):
                item_id = node.get_attr("id")
                item_label = node.get_attr("label")
                callback = bindings.get(item_id)

                btn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
                btn.set_label(item_label)
                if (callback):
                    btn.connect("clicked",
                                lambda x, cb:cb(), callback)
                menu.append(btn)

            elif (name == "choice"):
                choice_id = node.get_attr("id")
                choice_selected = int(node.get_attr("selected") or "0")
                callback = bindings.get(choice_id)
 
                group = None
                cnt = 0
                for option in node.get_children():
                    item_label = option.get_attr("label")
                    item_icon = option.get_attr("icon")
                    
                    btn = hildon.GtkRadioButton(gtk.HILDON_SIZE_AUTO, group)
                    btn.set_mode(False)
                    
                    if (callback):
                        btn.connect("clicked",
                                    lambda x, i, cb:cb(i), cnt, callback)
                    if (item_label):
                        btn.set_label(item_label)
                    if (item_icon):
                        img = gtk.Image()
                        img.set_from_pixbuf(getattr(theme, item_icon))
                        btn.set_image(img)

                    if (cnt == choice_selected):
                        btn.set_active(True)

                    menu.add_filter(btn)
                    group = btn
                    cnt += 1
                #end for
            #end if
        #end for

        menu.show_all()            
        self.__window.set_app_menu(menu)

