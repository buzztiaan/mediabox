"""
Base class for dialog components.
"""

from Component import Component
import msgs
from ui.Window import Window

import gtk


class Dialog(Component, Window):
    """
    Base class for dialog components.
    Dialogs can be brought up via the UI_ACT_SHOW_DIALOG(name) message.

    @since: 2009.11.17
    """
       
    def __init__(self):

        self.__title = ""
        self.__info = ""
        
       
        Component.__init__(self)
        Window.__init__(self, Window.TYPE_DIALOG)
        self.connect_closed(self.__on_close_window)
        
        
    def __on_close_window(self):
    
        self.set_visible(False)


    def set_visible(self, v):
    
        if (v):
            self.set_size(gtk.gdk.screen_width(),
                          gtk.gdk.screen_height() - 120)

        Window.set_visible(self, v)


    def set_title(self, title):
        """
        Sets the title text of the dialog.
        """
        
        Window.set_title(self, title)

