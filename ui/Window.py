from Widget import Widget
from ui.Pixmap import Pixmap
from ui import windowflags
import platforms

try:
    import gtk
except:
    gtk = None

try:
    import hildon
except:
    hildon = None


class Window(Widget):

    TYPE_TOPLEVEL = 0
    TYPE_DIALOG = 1

    RETURN_OK = 0
    RETURN_CANCEL = 1
    RETURN_YES = 2
    RETURN_NO = 3


    EVENT_CLOSED = "event-closed"
    

    def __init__(self, wtype):

        self.__wtype = wtype
        self.__flags = 0

        # window menu
        if (platforms.MAEMO5):
            self.__menu = hildon.AppMenu()
        else:
            self.__menu = gtk.Menu()
            
        # table: name -> menu_item
        self.__menu_items = {}

        self.__size = (0, 0)
        self.__has_size_set = False
        self.__is_button_pressed = False
        self.__screen = None
        
        Widget.__init__(self)

        if (wtype == self.TYPE_TOPLEVEL):
            if (platforms.MAEMO5):
                self.__window = hildon.StackableWindow()
                self.__window.set_app_menu(self.__menu)
            else:
                self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            
        elif (wtype == self.TYPE_DIALOG):
            self.__window = gtk.Dialog()

        self.__window.set_title(" ")
        self.__window.set_default_size(800, 480)
        self.__window.set_app_paintable(True)
        self.__window.set_double_buffered(False)

        self.__window.connect("configure-event", self.__on_configure)
        self.__window.connect("expose-event", self.__on_expose)
        self.__window.connect("button-press-event", self.__on_button_pressed)
        self.__window.connect("button-release-event", self.__on_button_released)
        self.__window.connect("motion-notify-event", self.__on_pointer_moved)
        self.__window.connect("key-press-event", self.__on_key_pressed)
        self.__window.connect("key-release-event", self.__on_key_released)
        self.__window.connect("delete-event", self.__on_close_window)

        self.__window.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                 gtk.gdk.BUTTON_RELEASE_MASK |
                                 gtk.gdk.POINTER_MOTION_MASK |
                                 gtk.gdk.POINTER_MOTION_HINT_MASK |
                                 gtk.gdk.KEY_PRESS_MASK |
                                 gtk.gdk.KEY_RELEASE_MASK)

        self.__window.realize()

        if (platforms.MAEMO5):
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)

        self.__layout = gtk.Fixed()
        self.__layout.show()
        if (wtype == self.TYPE_TOPLEVEL):
            self.__window.add(self.__layout)
        else:
            self.__window.vbox.add(self.__layout)
        
        # video screen
        self.__vidscreen = gtk.DrawingArea()
        self.__vidscreen.set_double_buffered(False)

        self.__vidscreen.modify_bg(gtk.STATE_NORMAL,
                                   gtk.gdk.color_parse("#000000"))
        self.__vidscreen.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                    gtk.gdk.BUTTON_RELEASE_MASK |
                                    gtk.gdk.POINTER_MOTION_MASK |
                                    gtk.gdk.KEY_PRESS_MASK |
                                    gtk.gdk.KEY_RELEASE_MASK)
        self.__layout.put(self.__vidscreen, 0, 0)


    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)


    def get_window(self):
    
        return self


    def set_flags(self, flags):
        """
        Sets the window flags.
        @since: 2010.02.12
        
        @param flags: window flags
        """

        changes = []
        for flag in [windowflags.FULLSCREEN,
                     windowflags.PORTRAIT,
                     windowflags.CATCH_VOLUME_KEYS,
                     windowflags.BUSY]:
            if (flags & flag != self.__flags &  flag):
                changes.append((flag, flags & flag))
        #end for
        self.__flags = flags

        for flag, value in changes:
            self._update_flag(flag, value)

        
    def set_flag(self, flag, value):
        """
        Sets or unsets a single window flag.
        @since: 2010.02.12
        
        @param flag: the flag to change
        @param value: whether to set (C{True}) or unset (C{False})
        """

        new_flags = self.__flags
        if (value):
            new_flags |= flag
        elif (self.__flags & flag):
            new_flags -= flag
        
        self.set_flags(new_flags)


    def __on_configure(self, src, ev):

        w, h = self.__window.get_size()
        if ((w, h) != self.__size):
            self.__screen = Pixmap(self.__window.window)
            self.set_screen(self.__screen)
            self.__size = (w, h)

            self.set_size(w, h)
            self.render()
        #end if
            

    def __on_expose(self, src, ev):
    
        if (self.__screen):
            x, y, w, h = ev.area
            self.__screen.restore(x, y, w, h)


    def __on_close_window(self, src, ev):
        
        self.emit_event(self.EVENT_CLOSED)
        return True


    def __on_button_pressed(self, src, ev):

        if (ev.button == 1):
            px, py = src.get_pointer()
            self._handle_event(self.EVENT_BUTTON_PRESS, px, py)
            self.__is_button_pressed = True

        return True

        
    def __on_button_released(self, src, ev):

        if (ev.button == 3):
            if (self.__menu_items):
                self.__menu.popup(None, None, None,
                                  ev.button, ev.get_time(), None)

        elif (ev.button == 1):
            if (self.__is_button_pressed):
                px, py = src.get_pointer()
                self._handle_event(self.EVENT_BUTTON_RELEASE, px, py)
                self.__is_button_pressed = False

        return True
        
        
    def __on_pointer_moved(self, src, ev):

        if (self.__is_button_pressed):
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

        self.emit_event(self.EVENT_KEY_PRESSED, key)
        
        # kill queued events
        if (key in ["Up", "Down", "Left", "Right"]):
            while (True):
                e = gtk.gdk.event_get()
                if (not e): break

        return False


    def __on_key_released(self, src, ev):

        keyval = ev.keyval
        c = gtk.gdk.keyval_to_unicode(keyval)
        if (c > 31):
            key = unichr(c)
        else:
            key = gtk.gdk.keyval_name(keyval)

        self.emit_event(self.EVENT_KEY_RELEASED, key)
                
        return False


    def __set_portrait_property(self, prop, value):

        self.__window.window.property_change(prop, "CARDINAL", 32,
                                             gtk.gdk.PROP_MODE_REPLACE,
                                             [value])


    def _update_flag(self, flag, value):

        if (flag == windowflags.FULLSCREEN):
            if (value):
                self.__window.fullscreen()
            else:
                self.__window.unfullscreen()

        elif (flag == windowflags.PORTRAIT):
            if (platforms.MAEMO5):
                self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
                self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST",
                                             value and 1 or 0)

        elif (flag == windowflags.BUSY):
            if (platforms.MAEMO5):
                hildon.hildon_gtk_window_set_progress_indicator(self.__window,
                                                              value and 1 or 0)

        elif (flag == windowflags.CATCH_VOLUME_KEYS):
            if (platforms.MAEMO5):
                self.__window.window.property_change("_HILDON_ZOOM_KEY_ATOM",
                                                     "XA_INTEGER", 32,
                                                     gtk.gdk.PROP_MODE_REPLACE,
                                                     [value and 1 or 0])




    def _get_window_impl(self):
    
        return self.__window


    def _visibility_changed(self):

        if (self.is_visible()):
            if (self.__wtype == self.TYPE_DIALOG and not self.__has_size_set):
                self.__window.resize(gtk.gdk.screen_width(),
                                     gtk.gdk.screen_height() - 120)
            self.__window.show()
            self.render()
        else:
            self.__window.hide()


    def set_parent_window(self, parent):
    
        self.__window.set_transient_for(parent._get_window_impl())


    def destroy(self):
    
        self.__window.destroy()


    def has_focus(self):

        return self.__window.has_focus
        

    def set_window_size(self, w, h):
    
        self.__window.resize(w, h)
        self.__has_size_set = True


    def set_title(self, title):
    
        self.__window.set_title(title)


    def set_menu_item(self, name, label, visible, cb):

        if (not name in self.__menu_items):
            if (platforms.MAEMO5):
                item = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
                item.set_label(label)
            else:
                item = gtk.MenuItem(label)
            self.__menu_items[name] = item
            self.__menu.append(item)
            if (platforms.MAEMO5):
                item.connect("clicked",
                             lambda src, cb: cb(),
                             cb)
            else:
                item.connect("activate",
                             lambda src, cb: cb(),
                             cb)   

        else:
            item = self.__menu_items[name]

        if (visible):
            item.show()
        else:
            item.hide()



    def set_menu_choice(self, name, icons_labels, selected, visible, cb):

        if (not name in self.__menu_items):
            group = None
            items = []
            cnt = 0
            for icon, label in icons_labels:
                if (platforms.MAEMO5):
                    item = hildon.GtkRadioButton(gtk.HILDON_SIZE_AUTO, group)
                    item.set_mode(False)
                else:
                    item = gtk.RadioMenuItem(group, label)
                
                if (icon):
                    if (platforms.MAEMO5):
                        img = gtk.Image()
                        img.set_from_pixbuf(icon)
                        item.set_image(img)                   

                elif (label):
                    if (platforms.MAEMO5):
                        item.set_label(label)
    
                if (not group): group = item
                items.append(item)
                if (platforms.MAEMO5):
                    self.__menu.add_filter(item)
                    item.connect("clicked",
                                 lambda src, cb, cnt: cb(cnt),
                                 cb, cnt)

                else:
                    self.__menu.append(item)
                    item.connect("activate",
                                 lambda src, cb, cnt: cb(cnt),
                                 cb, cnt)

                cnt += 1
            #end for
            self.__menu_items[name] = items

        else:
            items = self.__menu_items[name]

        for item in items:
            if (visible):
                item.show()
            else:
                item.hide()
        #end for

        items[selected].set_active(True)


    def put_widget(self, widget, x, y, w, h):

        if (not widget in self.__layout.get_children()):
            self.__layout.put(widget, x, y)
        else:
            self.__layout.move(widget, x, y)
        widget.set_size_request(w, h)


    def show_video_overlay(self, x, y, w, h):
    
        self.__layout.move(self.__vidscreen, x, y)
        self.__vidscreen.set_size_request(w, h)
        self.__vidscreen.show()
        
        return self.__vidscreen.window.xid


    def hide_video_overlay(self):
    
        self.__vidscreen.hide()


    def run(self):

        self.set_visible(True)
        while (self.is_visible()):
            gtk.main_iteration(True)
        #end while

