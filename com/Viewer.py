from Component import Component
import msgs
from ui.Widget import Widget


class Viewer(Component, Widget):

    PRIORITY = 0
    ICON = None
    ICON_ACTIVE = None
    

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
        """
        
        self.__current_tbar_set = widgets
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_TOOLBAR, self.__current_tbar_set)


    def set_title(self, title):
    
        self.__title = title
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_TITLE, title)
            

    def set_info(self, info):
    
        self.__info = info            
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_INFO, info)
            
            
    def set_collection(self, collection):
    
        self.__collection = collection
        if (self.__is_active):
            self.emit_event(msgs.CORE_ACT_SET_COLLECTION, collection)
            

    def show(self):
    
        self.set_visible(True)        
        self.__is_active = True
        
        self.set_toolbar(self.__current_tbar_set)
        self.set_collection(self.__collection)
        self.set_title(self.__title)
        self.set_info(self.__info)
        
        
    def hide(self):
    
        self.set_visible(False)
        self.__is_active = False


    def is_active(self):
    
        return self.__is_active

