from NativeWindow import NativeWindow
from ui import windowflags
from ui.Pixmap import Pixmap

import gtk


class Window(NativeWindow):

    def __init__(self, wtype):

        self.__menu = gtk.Menu()
        # table: name -> menu_item
        self.__menu_items = {}
        
    
        self.__size = (0, 0)
        self.__is_button_pressed = False
        self.__screen = None
        
        NativeWindow.__init__(self, wtype)
        
        self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
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


        self.__layout = gtk.Fixed()
        self.__layout.show()
        self.__window.add(self.__layout)
        
        # video screen
        self.__vidscreen = gtk.DrawingArea()
        self.__vidscreen.set_double_buffered(False)

        self.__vidscreen.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        self.__vidscreen.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                    gtk.gdk.BUTTON_RELEASE_MASK |
                                    gtk.gdk.POINTER_MOTION_MASK |
                                    gtk.gdk.KEY_PRESS_MASK |
                                    gtk.gdk.KEY_RELEASE_MASK)
        self.__layout.put(self.__vidscreen, 0, 0)


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
                self.__menu.popup(None, None, None, ev.button, ev.get_time(), None)

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


    def _update_flag(self, flag, value):

        if (flag == windowflags.FULLSCREEN):
            if (value):
                self.__window.fullscreen()
            else:
                self.__window.unfullscreen()


    def _get_window_impl(self):
    
        return self.__window


    def _visibility_changed(self):
    
        if (self.is_visible()):
            self.__window.show()
            self.render()
        else:
            self.__window.hide()


    def set_parent_window(self, parent):
    
        self.__window.set_transient_for(parent._get_window_impl())


    def destroy(self):
    
        self.__window.destroy()


    def set_window_size(self, w, h):
    
        self.__window.resize(w, h)


    def set_title(self, title):
    
        self.__window.set_title(title)


    def set_menu_item(self, name, label, visible, cb):

        if (not name in self.__menu_items):
            item = gtk.MenuItem(label)
            self.__menu_items[name] = item
            self.__menu.append(item)

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
                item = gtk.RadioMenuItem(group, label)
                if (not group): group = item
                items.append(item)
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



class XWindow(NativeWindow):

    def __init__(self, wtype):
    
        self.__is_button_pressed = False
    
        NativeWindow.__init__(self)
        self._init(wtype)
        
        
    def _init(self, wtype):
    
        if (wtype == self.TYPE_TOPLEVEL):
            self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            #self.__window.fullscreen()
            self.__window.set_default_size(800, 480)
        else:
            self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            #self.__window.set_decorated(False)
            #self.__window.fullscreen()
            self.__window.set_default_size(320,
                                           gtk.gdk.screen_height())
            self.__window.move(gtk.gdk.screen_width() - 320, 0)
            
        self._set_gtk_window(self.__window)
        self._setup_gtk_events()
        self._setup_gtk_rendering()
        overlay = self._create_gtk_video_overlay()
        self.__window.add(overlay)

        if (wtype == self.TYPE_DIALOG):
            self.__window.set_modal(True) #connect("focus-out-event", self.__on_close_window)


    def _set_gtk_window(self, win):

        self.__screen = None
        self.__menu = None
        self.__window = win
        
    
    def _setup_gtk_events(self):
        
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


    def _setup_gtk_rendering(self):

        self.__window.set_app_paintable(True)
        self.__window.set_double_buffered(False)


    def _create_gtk_video_overlay(self):

        self.__layout = gtk.Fixed()
        self.__layout.show()
        
        # video screen
        self.__vidscreen = gtk.DrawingArea()
        self.__vidscreen.set_double_buffered(False)

        scr = self.__vidscreen.get_screen()
        cmap = scr.get_rgb_colormap()
        self.__vidscreen.set_colormap(cmap)

        self.__vidscreen.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        self.__vidscreen.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                    gtk.gdk.BUTTON_RELEASE_MASK |
                                    gtk.gdk.POINTER_MOTION_MASK |
                                    gtk.gdk.KEY_PRESS_MASK |
                                    gtk.gdk.KEY_RELEASE_MASK)
        self.__layout.put(self.__vidscreen, 0, 0)

        return self.__layout



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
        self.__is_button_pressed = True
        return True

        
    def __on_button_released(self, src, ev):

        if (self.__is_button_pressed):
            px, py = src.get_pointer()
            self.emit_event(self.EVENT_BUTTON_RELEASED, px, py)
            self.__is_button_pressed = False
        return True
        
        
    def __on_pointer_moved(self, src, ev):

        if (self.__is_button_pressed):
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


    def __make_screen(self):
    
        w, h = self.__window.get_size()
        self.__screen = Pixmap(self.__window.window)


    def get_screen(self):
    
        if (not self.__screen):
            self.__make_screen()
        return self.__screen


    def set_visible(self, v):
    
        if (v):
            self.__window.present()
        else:
            self.__window.hide()


    def set_size(self, w, h):
    
        self.__window.resize(w, h)


    def set_title(self, title):
    
        self.__window.set_title(title)


    def get_window_impl(self):
    
        return self.__window


    def minimize(self):
    
        self.__window.iconify()


    def destroy(self):
    
        self.__window.destroy()


    def set_parent_window(self, other):
    
        self.__window.set_transient_for(other.get_window_impl())


    def show_menu(self):
    
        if (self.__menu):
            self.__menu.show_all()
            self.__menu.run()


    def set_menu_xml(self, xml, bindings):

        def click_cb(src, cb, *args):
            self.__menu.hide()
            cb(*args)

        dom = MiniXML(xml).get_dom()        
        self.__menu = gtk.Dialog()
        self.__menu.set_title("")
        vbox = self.__menu.vbox
        
        for node in dom.get_children():
            name = node.get_name()
            if (name == "item"):
                item_id = node.get_attr("id")
                item_label = node.get_attr("label")
                callback = bindings.get(item_id)

                btn = gtk.Button(item_label)
                btn.set_size_request(300, 80)
                if (callback):
                    btn.connect("clicked",
                                click_cb, callback)
                                #lambda x, cb:cb(), callback)
                vbox.add(btn)

            elif (name == "choice"):
                choice_id = node.get_attr("id")
                choice_selected = int(node.get_attr("selected") or "0")
                callback = bindings.get(choice_id)
 
                group = None
                hbox = gtk.HBox()
                vbox.add(hbox)
                cnt = 0
                for option in node.get_children():
                    item_label = option.get_attr("label")
                    item_icon = option.get_attr("icon")
                    
                    btn = gtk.ToggleButton()
                    
                    if (callback):
                        btn.connect("clicked",
                                    click_cb, callback, cnt)
                                    #lambda x, i, cb:cb(i), cnt, callback)
                    if (item_label):
                        btn.set_label(item_label)
                    if (item_icon):
                        img = gtk.Image()
                        img.set_from_pixbuf(getattr(theme, item_icon))
                        btn.set_image(img)

                    if (cnt == choice_selected):
                        btn.set_active(True)

                    hbox.add(btn)
                    group = btn
                    cnt += 1
                #end for
            #end if
        #end for


    def show_video_overlay(self, x, y, w, h):
    
        self.__layout.move(self.__vidscreen, x, y)
        self.__vidscreen.set_size_request(w, h)
        self.__vidscreen.show()
        
        return self.__vidscreen.window.xid


    def hide_video_overlay(self):
    
        self.__vidscreen.hide()


    def put_widget(self, widget, x, y):
    
        self.__layout.put(widget, x, y)


    def move_widget(self, widget, x, y):
    
        self.__layout.move(widget, x, y)

