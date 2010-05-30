"""
Base class for dialog components.
"""

from Component import Component
import msgs
import platforms
from ui import Window


class Dialog(Component, Window):
    """
    Base class for dialog components.
    Dialogs can be brought up via the UI_ACT_SHOW_DIALOG(name) message.
    Every dialog must have a unique class name among all dialogs. Alternatively,
    you may override the C{__repr__} method for returning a unique name.

    @since: 2009.11.17
    """
       
    def __init__(self):

        self.__title = ""
        self.__info = ""
        
        Component.__init__(self)
        Window.__init__(self, Window.TYPE_SUBWINDOW)
        self.connect_closed(self.__on_close_window)
   
        
    def __on_close_window(self):
    
        self.set_visible(False)

