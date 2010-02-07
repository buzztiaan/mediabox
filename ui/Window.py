from Widget import Widget
from TitleBar import TitleBar
import native
import platforms


class Window(Widget):

    TYPE_TOPLEVEL = 0
    TYPE_DIALOG = 1

    EVENT_CLOSED = "event-closed"


    def __init__(self, wtype):

        Widget.__init__(self)
        
        if (wtype == self.TYPE_TOPLEVEL):
            self.__native_window = native.Window(native.Window.TYPE_TOPLEVEL)
        else:
            self.__native_window = native.Window(native.Window.TYPE_DIALOG)
            
        self.__native_window.connect_closed(
                                lambda *a:self.emit_event(self.EVENT_CLOSED))
        self.__native_window.connect_button_pressed(self.__on_button_pressed)
        self.__native_window.connect_button_released(self.__on_button_released)
        self.__native_window.connect_pointer_moved(self.__on_pointer_moved)
        self.__native_window.connect_key_pressed(self.__on_key_pressed)
        self.__native_window.connect_screen_changed(self.__on_screen_changed)

        self.__container = Widget()
        self.__container.add(self)
        
        self.__title_bar = None
        if (not platforms.MAEMO5 and wtype == self.TYPE_TOPLEVEL):
            self.__title_bar = TitleBar()
            self.__title_bar.connect_close(
                                  lambda *a:self.emit_event(self.EVENT_CLOSED))
            self.__title_bar.connect_menu(
                                  lambda *a:self.__native_window.show_menu())
            self.__container.add(self.__title_bar)    
        #end if

        self.set_visible(False)


    def _visibility_changed(self):
    
        if (self.is_visible()):
            self.__native_window.set_visible(True)
            self.render()
        else:
            self.__native_window.set_visible(False)


    def __on_button_pressed(self, px, py):

        self.__container._handle_event(self.EVENT_BUTTON_PRESS, px, py)

        
    def __on_button_released(self, px, py):

        self.__container._handle_event(self.EVENT_BUTTON_RELEASE, px, py)


    def __on_pointer_moved(self, px, py):

        self.__container._handle_event(self.EVENT_MOTION, px, py)


    def __on_key_pressed(self, key):
    
        self.emit_event(self.EVENT_KEY_PRESSED, key)


    def __on_screen_changed(self):
    
        screen = self.__native_window.get_screen()
        self.__container.set_screen(screen)
        w, h = screen.get_size() 
        self.__container.set_size(w, h)

        if (self.__title_bar and self.__title_bar.is_visible()):
            self.__title_bar.set_geometry(0, 0, w, 57)
            self.set_geometry(0, 57, w, h - 57)
        else:
            self.set_geometry(0, 0, w, h)

        self.__container.render()

       
    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)
      
        
    def get_window(self):
    
        return self
        
        
    def get_native_window(self):
        """
        Returns the underlying native window implementation.
        """
    
        return self.__native_window
        
        
    def set_parent_window(self, other):
        """
        Sets a parent window for this window.
        """
    
        self.__native_window.set_parent_window(other.get_native_window())
        
        
        
    def destroy(self):
    
        self.set_visible(False)
        self.__native_window.destroy()
        
        
        
    def set_fullscreen(self, v):
    
        if (self.__title_bar):
            self.__title_bar.set_visible(not v)
        self.__native_window.set_fullscreen_mode(v)
        self.__on_screen_changed()
        
        
    def set_title(self, title):
        """
        Sets the window title.
        
        @param title: window title text
        """
    
        if (self.__title_bar):
            self.__title_bar.set_title(title)
        self.__native_window.set_title(title)


    def set_portrait_mode(self, v):
        """
        Switches between landscape and portrait mode on supported platforms.
        @since: 2009.09
        """
        
        self.__native_window.set_portrait_mode(v)
        self.__on_screen_changed()


    def set_busy(self, value):
        """
        Marks this window as busy. Depending on the platform this can e.g.
        change the mouse cursor or display a throbber animation in the title
        bar.
        @since: 2009.12.29
        
        @param value: whether this window is busy
        """
        
        self.__native_window.set_busy(value)


    def set_menu_xml(self, xml, bindings):
        """
        Sets the window menu from a XML description.
        @since 2009.11.19
        
        @param xml: XML description of the menu
        @param bindings: dictionary mapping XML node IDs to callback handlers
        """
        
        self.__native_window.set_menu_xml(xml, bindings)


    def show_video_overlay(self, x, y, w, h):
    
        return self.__native_window.show_video_overlay(x, y, w, h)
        
        
    def hide_video_overlay(self):
    
        self.__native_window.hide_video_overlay()



    def run(self):
        """
        Runs this window until it gets closed.
        """
    
        import gtk
        self.set_visible(True)
        while (self.is_visible()):
            gtk.main_iteration(True)
        #end while

