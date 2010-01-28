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
        
        if (platforms.MAEMO5):
            self.__title_bar = None
        else:
            self.__title_bar = TitleBar()
            self.__title_bar.connect_button_released(self.__on_click_title_bar)
            self.__container.add(self.__title_bar)    

        self.set_visible(False)


    def _visibility_changed(self):
    
        if (self.is_visible()):
            #self.__window.show()
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

        if (self.__title_bar):
            self.__title_bar.set_geometry(0, 0, w, 64)
            self.set_geometry(0, 64, w, h - 64)
        else:
            self.set_geometry(0, 0, w, h)

        self.__container.render()


    def __on_click_title_bar(self, px, py):
    
        w, h = self.__title_bar.get_size()
        if (px > w - 64):
            self.emit_event(self.EVENT_CLOSED)
        else:
            self.__native_window.show_menu()

        
    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)

        
    def put(self, w, x, y):
    
        pass
        
        
    def move(self, w, x, y):
    
        pass
        
        
    def get_window(self):
    
        return self
        
        
    def get_native_window(self):
    
        return self.__native_window
        
        
    def set_parent_window(self, other):
    
        self.__native_window.set_parent_window(other.get_native_window())
        
        
    def set_fullscreen(self, v):
    
        pass
        
        
    def set_title(self, title):
    
        if (self.__title_bar):
            self.__title_bar.set_title(title)
        self.__native_window.set_title(title)


    def set_portrait_mode(self, v):
        """
        Switches between landscape and portrait mode on supported platforms.
        @since: 2009.09
        """
        
        self.__native_window.set_portrait_mode(v)


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

