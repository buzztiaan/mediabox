from utils.Observable import Observable
from mediabox import caps
import theme


class Viewer(Observable):
    """
    Abstract base class for media viewers.
    """
    
    ICON = theme.dialog_error
    ICON_ACTIVE = theme.viewer_none_active
    PRIORITY = 999
    CAPS = caps.NONE
    BORDER_WIDTH = 6
    
    
    OBS_TITLE = 0    
    OBS_POSITION = 1
    OBS_FREQUENCY_MHZ = 2
    OBS_VOLUME = 3

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
    
    OBS_STATE_PLAYING = 100
    OBS_STATE_PAUSED = 101
    
    OBS_MINIMIZE = 200
    OBS_QUIT = 201
    
    
    
    def __init__(self):
    
        self.__widget = None
        self.__is_active = False
        self.__title = ""

        
        
    def __repr__(self):
    
        return self.__class__.__name__
        
        
    def is_available(self):
    
        return True


    def shutdown(self):
    
        pass


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
        
        
    def previous(self):
    
        pass
        
    
    def next(self):
    
        pass
        

    def add(self):
    
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
        
