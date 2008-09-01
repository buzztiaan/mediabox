"""
Base class for viewer components.
"""

from Component import Component
import msgs
from ui.Widget import Widget


class Viewer(Component, Widget):
    """
    Components derived from this class appear with an icon in the viewer menu
    and can be selected by the user.
    
    Example::

      from com import Viewer, msgs
      import theme
      
      class MyViewer(Viewer):
      
          ICON = theme.myviewer_icon
          PRIORITY = 500
      
          def __init__(self):
          
              Viewer.__init__(self)
              
          def handle_event(self, msg, *args):
          
              ...
    """
    
    PRIORITY = 0
    """
    The priority determines the position of the icon in the viewer menu. All
    viewers are sorted by priority.
    """
    ICON = None
    """
    The specified icon is used for representing the viewer in the viewer menu.
    """
    

    def __init__(self):
    
        self.__is_active = False
        
        self.__current_tbar_set = []
        self.__collection = []
        self.__title = ""
        self.__info = ""
        
        Component.__init__(self)
        Widget.__init__(self)


    def set_toolbar(self, widgets):
        """
        Sets the toolbar from the given widgets.
        
        @param widgets: list of widgets
        """
        
        self.__current_tbar_set = widgets
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_TOOLBAR, self.__current_tbar_set)


    def set_title(self, title):
        """
        Sets the viewer title to the given text.
        
        @param title: title string
        """
    
        self.__title = title
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_TITLE, title)
            

    def set_info(self, info):
        """
        Sets the viewer info text to the given text.
        
        @param info: info string
        """
    
        self.__info = info            
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_INFO, info)
            
            
    def set_collection(self, collection):
        """
        Sets the collection of media items that is shown in the side strip.
        
        @param collection: list of items (derived from L{ui.StripItem})
        """
    
        self.__collection = collection
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_COLLECTION, collection)
            

    def show(self):
        """
        This method gets called when the viewer becomes visible. If you need
        to take action at this point, you may override this method but do
        not forget to call this method on the super class as well.
        """
    
        self.set_visible(True)        
        self.__is_active = True
        
        self.set_toolbar(self.__current_tbar_set)
        self.set_collection(self.__collection)
        self.set_title(self.__title)
        self.set_info(self.__info)
        
        
    def hide(self):
        """
        This method gets called when the viewer gets hidden. If you need
        to take action at this point, you may override this method but do
        not forget to call this method on the super class as well.
        """
        
        self.set_visible(False)
        self.__is_active = False


    def is_active(self):
        """
        Returns whether this viewer is currently the active viewer. There is
        only one viewer active at a time.
        
        @return: whether this viewer is active
        """
    
        return self.__is_active



    def fx_slide_out(self, wait = True):
    
        import threading
        import gobject
        import gtk
           
        STEP = 20
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        finished = threading.Event()
        
        def f(i):
            screen.move_area(x, y, w - STEP, h, STEP, 0)
            screen.fill_area(x, y, STEP, h, "#ffffff")
            #screen.copy_pixmap(self.__buffer, 0, h - i - STEP, 0, 0, w, STEP)
            if (i < w - STEP):
                gobject.timeout_add(2, f, i + STEP)
            else:
                finished.set()
                
        self.set_events_blocked(True)
        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration(False)        
        self.set_events_blocked(False)
