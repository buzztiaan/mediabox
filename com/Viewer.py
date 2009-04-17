"""
Base class for viewer components.
"""

from Component import Component
import msgs
from ui.Widget import Widget


class Viewer(Component, Widget):
    """
    Base class for viewer components.
    Components derived from this class appear with an icon in the viewer menu
    and can be selected by the user.
    
    Example::

      from com import Viewer, msgs
      from theme import theme
      
      class MyViewer(Viewer):
      
          ICON = theme.myviewer_icon
          PRIORITY = 500
      
          def __init__(self):
          
              Viewer.__init__(self)
              
          def handle_message(self, msg, *args):
          
              ...

    @since: 0.96
    """
    
    PRIORITY = 0
    """
    The priority determines the position of the icon in the viewer menu. All
    viewers are sorted by priority.
    @since: 0.96
    """
    ICON = None
    """
    The specified icon is used for representing the viewer in the viewer menu.
    @since: 0.96
    """
    

    def __init__(self):
    
        self.__is_active = False
        
        self.__current_tbar_set = []
        self.__title = ""
        self.__info = ""
        
       
        Component.__init__(self)
        Widget.__init__(self)



    def set_toolbar(self, widgets):
        """
        Sets the toolbar from the given widgets.
        @since: 0.96
        
        @param widgets: list of widgets
        """
        
        self.__current_tbar_set = widgets
        if (self.__is_active):
            self.emit_message(msgs.CORE_ACT_SET_TOOLBAR, self.__current_tbar_set)


    def set_title(self, title):
        """
        Sets the viewer title to the given text.
        @since: 0.96
        
        @param title: title string
        """
    
        self.__title = title
        if (self.__is_active):
            self.emit_message(msgs.CORE_ACT_SET_TITLE, title)
            

    def set_info(self, info):
        """
        Sets the viewer info text to the given text.
        @since: 0.96
        
        @param info: info string
        """
    
        self.__info = info            
        if (self.__is_active):
            self.emit_message(msgs.CORE_ACT_SET_INFO, info)
            
            
    def set_strip(self, collection):
        """
        Sets the collection of media items that is shown in the side strip.
        @since: 0.96
        
        @param collection: list of items (derived from L{ui.StripItem})
        """
    
        #self.__collection = collection
        self.emit_message(msgs.UI_ACT_SET_STRIP, self, collection)


    def change_strip(self, owner):
        """
        Switches the contents of the side strip to the items of the given
        owner.
        @since: 0.96
        
        @param owner: owner object
        """
        
        self.emit_message(msgs.UI_ACT_CHANGE_STRIP, owner)
    

            
    def hilight_strip_item(self, idx):
        """
        Hilights the given item in the side strip.
        @since: 0.96
        
        @param idx: index of the item to hilight
        """
        
        self.emit_message(msgs.UI_ACT_HILIGHT_STRIP_ITEM, self, idx)
            
            
    def select_strip_item(self, idx):
        """
        Selects the given item in the side strip.
        @since: 0.96
        
        @param idx: index of the item to select
        """
        
        self.emit_message(msgs.UI_ACT_SELECT_STRIP_ITEM, self, idx)
            
            
    def show_strip_item(self, idx):
        """
        Scrolls to the given item in the side strip.
        @since: 0.96
        
        @param idx: index of the item to scroll to
        """
        
        self.emit_message(msgs.UI_ACT_SHOW_STRIP_ITEM, self, idx)
        
            

    def show(self):
        """
        This method gets called when the viewer becomes visible. If you need
        to take action at this point, you may override this method but do
        not forget to call this method on the super class as well.
        @since: 0.96
        """
    
        self.set_visible(True)        
        self.__is_active = True
        
        print self.__current_tbar_set
        self.set_toolbar(self.__current_tbar_set)
        #self.set_strip(self.__collection)
        self.set_title(self.__title)
        self.set_info(self.__info)
        
        
    def hide(self):
        """
        This method gets called when the viewer gets hidden. If you need
        to take action at this point, you may override this method but do
        not forget to call this method on the super class as well.
        @since: 0.96
        """
        
        self.set_visible(False)
        self.__is_active = False


    def is_active(self):
        """
        Returns whether this viewer is currently the active viewer. There is
        only one viewer active at a time.
        @since: 0.96
        
        @return: whether this viewer is active
        """
    
        return self.__is_active

