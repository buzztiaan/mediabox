from utils.EventEmitter import EventEmitter


class NativeWindow(EventEmitter):

    TYPE_TOPLEVEL = 0
    TYPE_DIALOG = 1

    EVENT_CLOSED = "event-closed"
    EVENT_BUTTON_PRESSED = "event-button-pressed"
    EVENT_BUTTON_RELEASED = "event-button-released"
    EVENT_POINTER_MOVED = "event-pointer-moved"
    EVENT_KEY_PRESSED = "event-key-pressed"
    EVENT_KEY_RELEASED = "event-key-released"
    EVENT_SCREEN_CHANGED = "event-screen-changed"
    

    def __init__(self):
    
        EventEmitter.__init__(self)


    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)


    def connect_screen_changed(self, cb, *args):
    
        self._connect(self.EVENT_SCREEN_CHANGED, cb, *args)


    def connect_button_pressed(self, cb, *args):
    
        self._connect(self.EVENT_BUTTON_PRESSED, cb, *args)


    def connect_button_released(self, cb, *args):
    
        self._connect(self.EVENT_BUTTON_RELEASED, cb, *args)


    def connect_pointer_moved(self, cb, *args):
    
        self._connect(self.EVENT_POINTER_MOVED, cb, *args)


    def connect_key_pressed(self, cb, *args):
    
        self._connect(self.EVENT_KEY_PRESSED, cb, *args)


    def connect_key_released(self, cb, *args):
    
        self._connect(self.EVENT_KEY_RELEASED, cb, *args)


    def get_screen(self):
    
        raise NotImplementedError


    def set_visible(self, v):
    
        raise NotImplementedError


    def set_title(self, title):
        
        pass


    def set_parent_window(self, other):
        
        pass


    def get_window_impl(self):
    
        raise NotImplementedError


    def destroy(self):
    
        raise NotImplementedError

    
    def set_fullscreen_mode(self, v):
    
        pass


    def set_portrait_mode(self, v):
    
        pass


    def set_busy(self, v):
    
        pass
        

    def show_menu(self):
    
        pass

        
    def set_menu_xml(self, xml, bindings):
        """
        Sets the window menu from a XML description.
        @since 2009.11.19
        
        @param xml: XML description of the menu
        @param bindings: dictionary mapping XML node IDs to callback handlers
        """
        
        raise NotImplementedError


    def show_video_overlay(self, x, y, w, h):
    
        raise NotImplementedError
        
        
    def hide_video_overlay(self):
    
        raise NotImplementedError

