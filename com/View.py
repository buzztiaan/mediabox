"""
Base class for view components.
"""

from Component import Component
import msgs
from ui.Widget import Widget


class View(Component, Widget):
    """
    Base class for view components.
    Components derived from this class appear as tabs in the application.
    
    Example::

      from com import View, msgs
      from theme import theme
      
      class MyView(View):
      
          ICON = theme.myview_icon
          PRIORITY = 500
      
          def __init__(self):
          
              View.__init__(self)
              

    @since: 0.97
    """
    
    TITLE = ""
    """
    Title of the view. The title will be visible on the tab.
    """
    
    PRIORITY = 0
    """
    The priority determines the position of the tab. All views are sorted by
    priority.
    """
    

    def __init__(self):
    
        self.__is_active = False
        
        self.__title = ""
        self.__info = ""
        
       
        Component.__init__(self)
        Widget.__init__(self)


    def show(self):
        """
        This method gets called when the view becomes visible. If you need
        to take action at this point, you may override this method but do
        not forget to call this method on the super class as well.
        """
    
        self.set_visible(True)        
        self.__is_active = True
        
       
        
    def hide(self):
        """
        This method gets called when the view gets hidden. If you need
        to take action at this point, you may override this method but do
        not forget to call this method on the super class as well.
        """
        
        self.set_visible(False)
        self.__is_active = False


    def is_active(self):
        """
        Returns whether this view is currently the active view. There is
        only one view active at a time.
        
        @return: whether this view is active
        """
    
        return self.__is_active

