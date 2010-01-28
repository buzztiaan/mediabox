from NativeWindow import NativeWindow
from ui.Pixmap import Pixmap
from utils.MiniXML import MiniXML
from theme import theme

import gtk
import hildon


class Window(NativeWindow):

    def __init__(self, wtype):
    
        self.__screen = None
    
        NativeWindow.__init__(self)
        
        if (wtype == self.TYPE_TOPLEVEL):
            self.__window = hildon.StackableWindow()
            
        elif (wtype == self.TYPE_DIALOG):
            self.__window = gtk.Dialog()
                
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

        self.__window.set_app_paintable(True)
        self.__window.set_double_buffered(False)
        self.__window.realize()


        self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)

        # we need to notify Maemo5 that we want to use the volume keys
        self.__window.window.property_change("_HILDON_ZOOM_KEY_ATOM",
                                                "XA_INTEGER", 32,
                                                gtk.gdk.PROP_MODE_REPLACE,
                                                [1])


    def __on_configure(self, src, ev):
    
        w, h = self.__window.get_size()
        if (self.__screen and (w, h) != (self.__screen.get_size())):
            self.__screen = None
            self.emit_event(self.EVENT_SCREEN_CHANGED)

        elif (not self.__screen and w > 10 and h > 10):
            self.emit_event(self.EVENT_SCREEN_CHANGED)
            

    def __on_expose(self, src, ev):
    
        if (self.__screen):
            x, y, w, h = ev.area
            self.__screen.restore(x, y, w, h)


    def __on_close_window(self, src, ev):
        
        self.emit_event(self.EVENT_CLOSED)
        return True


    def __on_button_pressed(self, src, ev):

        px, py = src.get_pointer()
        self.emit_event(self.EVENT_BUTTON_PRESSED, px, py)
        return True

        
    def __on_button_released(self, src, ev):

        px, py = src.get_pointer()
        self.emit_event(self.EVENT_BUTTON_RELEASED, px, py)
        return True
        
        
    def __on_pointer_moved(self, src, ev):

        px, py = src.get_pointer()
        self.emit_event(self.EVENT_POINTER_MOVED, px, py)
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

        return True


    def __on_key_released(self, src, ev):

        keyval = ev.keyval
        c = gtk.gdk.keyval_to_unicode(keyval)
        if (c > 31):
            key = unichr(c)
        else:
            key = gtk.gdk.keyval_name(keyval)

        self.emit_event(self.EVENT_KEY_RELEASED, key)
                
        return True


    def __make_screen(self):
    
        w, h = self.__window.get_size()
        self.__screen = Pixmap(self.__window.window)


    def get_screen(self):
    
        if (not self.__screen):
            self.__make_screen()
        return self.__screen


    def set_visible(self, v):
    
        if (v):
            self.__window.resize(gtk.gdk.screen_width(),
                                 gtk.gdk.screen_height() - 120)
            self.__window.present()
        else:
            self.__window.hide()


    def set_title(self, title):
    
        self.__window.set_title(title)


    def get_window_impl(self):
    
        return self.__window


    def set_parent_window(self, other):
    
        self.__window.set_transient_for(other.get_window_impl())


    def __set_portrait_property(self, prop, value):

        self.__window.window.property_change(prop, "CARDINAL", 32,
                                             gtk.gdk.PROP_MODE_REPLACE,
                                             [value])


    def set_portrait_mode(self, v):
        
        if (v):
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST", 1)
        else:
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST", 0)


    def set_busy(self, value):
        
        hildon.hildon_gtk_window_set_progress_indicator(self.__window,
                                                        value and 1 or 0) 


    def set_menu_xml(self, xml, bindings):
    
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

