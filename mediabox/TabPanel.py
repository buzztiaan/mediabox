from ui.Widget import Widget
from ui.HBox import HBox
from ui.ImageButton import ImageButton
from ui.SequenceButton import SequenceButton
from ui.Label import Label
from ui.Pixmap import Pixmap
from ui import pixbuftools
from utils.Observable import Observable
import config as mb_config
import values
import theme

import threading
import gtk
import gobject


class TabPanel(Widget, Observable):

    OBS_TAB_SELECTED = 0
    OBS_SHUFFLE_MODE = 1
    OBS_REPEAT_MODE = 2
    

    def __init__(self):
    
        self.__buffer = Pixmap(None, 800, 480)
           
        # the currently selected tab
        self.__index = 0
        
        # the index of the component that is currently playing
        self.__currently_playing = -1
        
        self.__lock = threading.Event()
        
        self.__pos = (0, 0)
        
        # icon widgets
        self.__icons = []
        self.__viewers = []

        
        Widget.__init__(self)
        self.__label = Label("%s ver %s - %s" \
                      % (values.NAME, values.VERSION, values.COPYRIGHT),
                      theme.font_micro, theme.color_fg_splash)
        self.add(self.__label)
        self.__label.set_alignment(self.__label.RIGHT)

        # playmode buttons
        repeat_mode = mb_config.repeat_mode()
        shuffle_mode = mb_config.shuffle_mode()

        btn_repeat = SequenceButton(
             [(theme.mb_repeat_none, mb_config.REPEAT_MODE_NONE),
              (theme.mb_repeat_one, mb_config.REPEAT_MODE_ONE),
              (theme.mb_repeat_all, mb_config.REPEAT_MODE_ALL)])
        btn_repeat.connect_changed(
              lambda v:self.update_observer(self.OBS_REPEAT_MODE, v))
        btn_repeat.set_pos(730, 30)
        btn_repeat.set_value(repeat_mode)
        self.add(btn_repeat)
        
        btn_shuffle = SequenceButton(
             [(theme.mb_shuffle_none, mb_config.SHUFFLE_MODE_NONE),
              (theme.mb_shuffle_one, mb_config.SHUFFLE_MODE_ONE)])
        btn_shuffle.connect_changed(
              lambda v:self.update_observer(self.OBS_SHUFFLE_MODE, v))
        btn_shuffle.set_pos(730, 100)
        btn_shuffle.set_value(shuffle_mode)
        self.add(btn_shuffle)


    def _reload(self):
    
        self.__icons[self.__index].set_active(False)
    
        viewers = self.__viewers
        self.__pos = (0, 0)
        self.__icons = []
        self.__viewers = []
        
        for v in viewers:
            self.add_viewer(v)


    def __on_tab_selected(self, px, py, idx):

        if (self.__lock.isSet()): return

        self.select_viewer(idx)
        self.update_observer(self.OBS_TAB_SELECTED, idx)


    def add_viewer(self, v):
    
        self.__viewers.append(v)
        x, y = self.__pos        
                
        icon_active = pixbuftools.make_frame(theme.mb_selection_frame,
                                             120, 120, True)
        pixbuftools.draw_pbuf(icon_active, v.ICON, 0, 0)
        
        icon = ImageButton(v.ICON, icon_active, manual = True)
        icon.set_size(120, 120)
        self.add(icon)
        if (len(self.__icons) == self.__index):
            icon.set_active(True)
        icon.connect_button_pressed(self.__on_tab_selected, len(self.__icons))
        self.__icons.append(icon)
        
        offx = (128 - v.ICON.get_width()) / 2
        offy = (128 - v.ICON.get_height()) / 2
        icon.set_pos(10 + x * 128 + offx, 10 + y * 128 + offy)

        height = (y + 1) * 130 + 20
        self.set_geometry(0, 480 - height, 800, height)
        self.__label.set_geometry(0, height - 16, 790, 0)

        x += 1
        if (x == 5):
            x = 0
            y += 1
        self.__pos = (x, y)


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
       
        screen.fill_area(x, y, w - 80, h, theme.color_bg)
        screen.fill_area(w - 80, y, 80, h, "#aaaaaf")
        screen.fill_area(0, 0, w, 2, "#333333")
        
        if (self.__currently_playing >= 0):
            icon = self.__icons[self.__currently_playing]
            i_x, i_y = icon.get_screen_pos()
            screen.draw_pixbuf(theme.mb_btn_load, i_x + 120 - 32, i_y)


    def select_viewer(self, idx):

        if (idx != self.__index):            
            icon = self.__icons[self.__index]
            icon.set_active(False)
 
            icon = self.__icons[idx]
            icon.set_active(True)
            
            self.__index = idx    


    def set_currently_playing(self, idx):
    
        self.__currently_playing = idx
        
        
    def close(self):

        self.select_viewer(self.__index)
        self.update_observer(self.OBS_TAB_SELECTED, self.__index)


    def fx_raise(self, wait = True):
    
        if (self.__lock.isSet()): return
        self.__lock.set()

        STEP = 10
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)
        self.render_at(buf)       
        self.__buffer.copy_pixmap(screen, 0, 0, 0, 0, 800, h)
        finished = threading.Event()
        
        
        def f(i):
            screen.move_area(0, STEP, 800, 480 - i, 0, -STEP)
            screen.copy_pixmap(buf, 0, h - i, 0, 480 - i, w, STEP)
            if (i < h):
                gobject.timeout_add(2, f, i + STEP)
            else:
                finished.set()
                self.__lock.clear()
                
        self.set_events_blocked(True)
        f(STEP)
        while (wait and not finished.isSet()): gtk.main_iteration(False)        
        gobject.timeout_add(250, self.set_events_blocked, False)


    def fx_lower(self, wait = True):

        if (self.__lock.isSet()): return
        self.__lock.set()
    
        STEP = 10
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        finished = threading.Event()
        
        def f(i):
            screen.move_area(0, 0, 800, 480 - h + i, 0, STEP)
            screen.copy_pixmap(self.__buffer, 0, h - i - STEP, 0, 0, w, STEP)
            if (i < h - STEP):
                gobject.timeout_add(2, f, i + STEP)
            else:
                finished.set()
                self.__lock.clear()
                
        self.set_events_blocked(True)
        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration(False)        
        gobject.timeout_add(250, self.set_events_blocked, False)

