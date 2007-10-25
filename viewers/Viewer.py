from utils.Observable import Observable
from mediabox import caps


class Viewer(Observable):
    """
    Abstract base class for media viewers.
    """
    
    ICON = "gfx/dialog-error.png"
    PRIORITY = 999
    CAPS = caps.NONE
    BORDER_WIDTH = 6
    
    # override this with False if your viewer is running fine
    # experimental viewers are not visible by default
    IS_EXPERIMENTAL = True
    
    OBS_TITLE = 0    
    OBS_POSITION = 1
    OBS_VOLUME = 2

    OBS_REPORT_CAPABILITIES = 10    
    OBS_SET_COLLECTION = 11
    OBS_SCAN_MEDIA = 12
    
    OBS_SHOW_COLLECTION = 20
    OBS_HIDE_COLLECTION = 21       
    OBS_FULLSCREEN = 22
    OBS_UNFULLSCREEN = 23
    
    OBS_SHOW_MESSAGE = 30
    OBS_SHOW_PROGRESS = 31
    OBS_SHOW_PANEL = 32
    
    
    
    def __init__(self):
    
        self.__widget = None
        self.__is_active = False
        self.__title = ""

        
        
    def __repr__(self):
    
        return self.__class__.__name__
        
        
    def clear_items(self):
    
        pass
        
        
    def make_item_for(self, uri, thumbnailer):
    
        return None        
        
        
    def load(self, uri):
    
        pass
        
        
    def increment(self):
    
        pass
        
        
    def decrement(self):
    
        pass
        
        
    def set_position(self, percentpos):
    
        pass


    def play_pause(self):
    
        pass


    def set_widget(self, widget):
    
        self.__widget = widget
        
        
    def get_widget(self):
    
        return self.__widget
        
        
    def show(self):
    
        self.__widget.show()
        self.__is_active = True
        self.update_observer(self.OBS_REPORT_CAPABILITIES, self.CAPS)
        self.update_observer(self.OBS_TITLE, self.__title)
        self.update_observer(self.OBS_POSITION, 0, 0)
        
        
    def hide(self):
    
        self.__widget.hide()
        self.__is_active = False
        self.update_observer(self.OBS_SHOW_COLLECTION)
        
        
    def fullscreen(self):
    
        pass
        
        
    def is_active(self):
    
        return self.__is_active


    def set_title(self, title):
    
        self.__title = title
        self.update_observer(self.OBS_TITLE, title)
        
