from utils.Observable import Observable
from mediabox import caps
import theme
from ui.Widget import Widget
from ui.Pixmap import Pixmap

import gtk
import gobject
import threading


class Viewer(Widget, Observable):
    """
    Abstract base class for media viewers.
    """
    
    ICON = None
    ICON_ACTIVE = None
    PRIORITY = 999
    CAPS = caps.NONE
    
    
    OBS_TITLE = 0    
    OBS_POSITION = 1
    OBS_TIME = 2
    OBS_FREQUENCY_MHZ = 3
    OBS_VOLUME = 4

    OBS_REPORT_CAPABILITIES = 10    
    OBS_SET_COLLECTION = 11
    OBS_SELECT_ITEM = 12
    OBS_SCAN_MEDIA = 13
    
    OBS_SHOW_COLLECTION = 20
    OBS_HIDE_COLLECTION = 21       
    OBS_FULLSCREEN = 22
    OBS_UNFULLSCREEN = 23
    OBS_RENDER = 24
    
    OBS_SHOW_MESSAGE = 30
    OBS_SHOW_PROGRESS = 31
    OBS_SHOW_PANEL = 32
    
    OBS_STOP_PLAYING = 40
    
    OBS_STATE_PLAYING = 100
    OBS_STATE_PAUSED = 101
    
    OBS_MINIMIZE = 200
    OBS_QUIT = 201
    
    
    
    def __init__(self, esens):
    
        self.__is_active = False
        self.__title = ""
        
        Widget.__init__(self, esens)
    
        
    def __repr__(self):
    
        return self.__class__.__name__
     
 
    def is_available(self):
    
        return True


    def shutdown(self):
    
        pass


    def clear_items(self):
    
        pass
        
    
    def update_media(self, mscanner):
    
        pass
        
        
    def load(self, uri):
    
        pass
       
    def search(self, key):
    
        pass
        
        
    def do_enter(self):
    
        pass
        
        
    def do_increment(self):
    
        pass
        
        
    def do_decrement(self):
    
        pass
        
        
    def do_set_position(self, percentpos):
    
        pass


    def do_play_pause(self):
    
        pass
        
        
    def do_zoom_in(self):
    
        pass
        

    def do_zoom_out(self):
    
        pass


    def do_zoom_100(self):
    
        pass


    def do_zoom_fit(self):
    
        pass

        
    def do_previous(self):
    
        pass
        
    
    def do_next(self):
    
        pass
        

    def do_add(self):
    
        pass


    def do_toggle_speaker(self):
    
        pass
     
     
    def do_toggle_playlist(self):
     
        pass
     
        
    def show(self):
    
        self.set_visible(True)
        self.__is_active = True
        
        
    def hide(self):
    
        self.set_visible(False)
        self.__is_active = False
        
        
    def stop_playing(self, issued_by):
    
        pass
        
        
    def do_fullscreen(self):
    
        pass
        
        
    def is_active(self):
    
        return self.__is_active


    def set_title(self, title):
    
        self.__title = title
        self.update_observer(self.OBS_TITLE, title)


    def fx_slide_out(self, wait = True):
    
        STEP = 31
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        finished = threading.Event()
    
        def fx(i):
            screen.copy_pixmap(screen, x, y, x + STEP, y, w - STEP, h)
            screen.draw_subpixbuf(theme.background, x + i, y, x + i, y, STEP, h)
            if (i < w - STEP):
                gobject.timeout_add(5, fx, i + STEP)
            else:
                finished.set()
        
        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration()



    def fx_slide_in(self, wait = True):
    
        STEP = 20
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        finished = threading.Event()
        
        def f(i):
            screen.copy_pixmap(buf, i, 0, x + w - STEP, y, STEP, h)
            if (i < w - STEP):
                screen.copy_pixmap(screen, x + w - i - STEP, y, x + w - i - STEP - STEP,
                                   y, i + STEP, h)
            if (i < w - STEP):
                gobject.timeout_add(5, f, i + STEP)
            else:
                finished.set()
                
        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration()
        
