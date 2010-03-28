from ui import Widget
from ui import windowflags
from utils.EventEmitter import EventEmitter


class NativeWindow(Widget):

    TYPE_TOPLEVEL = 0
    TYPE_DIALOG = 1

    RETURN_OK = 0
    RETURN_CANCEL = 1
    RETURN_YES = 2
    RETURN_NO = 3


    EVENT_CLOSED = "event-closed"

    def __init__(self, wtype):
    
        self.__flags = 0

        Widget.__init__(self)


    def connect_closed(self, cb, *args):
    
        self._connect(self.EVENT_CLOSED, cb, *args)
      
        
    def get_window(self):
    
        return self
        
        
    def _get_window_impl(self):
    
        raise NotImplementedError


    def set_parent_window(self, other):
        """
        Sets a parent window for this window.
        """
    
        pass
        
        
    def destroy(self):
    
        raise NotImplementedError


    def set_window_size(self, w, h):
        """
        Sets the window size, if supported by the native window implementation.
        
        @param w: width
        @param h: height
        """
    
        raise NotImplementedError


    def _update_flag(self, flag, value):
    
        raise NotImplementedError


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

        
    def set_title(self, title):
        """
        Sets the window title.
        
        @param title: window title text
        """
    
        raise NotImplementedError


    def set_menu_item(self, name, label, visible, cb):

        raise NotImplementedError


    def set_menu_choice(self, name, icons_labels, selected, visible, cb):

        raise NotImplementedError


    def put_widget(self, widget, x, y, w, h):

        raise NotImplementedError
        

    def show_video_overlay(self, x, y, w, h):
    
        raise NotImplementedError
        
        
    def hide_video_overlay(self):
    
        raise NotImplementedError



    def run(self):
        """
        Runs this window until it gets closed. Returns a return code.
        """
    
        raise NotImplementedError
        

