"""
Base class for view components.
"""

from Component import Component
import msgs
from ui.Widget import Widget


class View(Component, Widget):
    """
    Base class for view components.

    @since: 0.97
    """
    
    TITLE = ""
    """
    Title of the view. The title will be visible on the tab.
    """
    
    def __init__(self):

        self.__title = ""
        self.__info = ""
        
       
        Component.__init__(self)
        Widget.__init__(self)



    def is_active(self):
        """
        Returns whether this view is currently the active view. There is
        only one view active at a time.
        
        @return: whether this view is active
        """
    
        return self.is_visible()

