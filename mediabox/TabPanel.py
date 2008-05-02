from ui.Widget import Widget
from ui.HBox import HBox
from ui.Image import Image
from ui.Label import Label
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
from utils.Observable import Observable
import values
import theme

import threading
import gtk
import gobject


class TabPanel(Widget, Observable):

    OBS_TAB_SELECTED = 0
    

    def __init__(self, esens):
    
        self.__buffer = Pixmap(None, 800, 480)
        
    
        # the currently selected tab
        self.__index = 0
        
        self.__lock = threading.Event()
        
        self.__esens = esens
        self.__pos = (0, 0)
        
        # icon widgets
        self.__icons = []
        
        # images
        self.__images = []
        
        Widget.__init__(self, esens)
        self.__label = Label(esens,
                      "%s ver %s - %s" \
                      % (values.NAME, values.VERSION, values.COPYRIGHT),
                      theme.font_micro, theme.color_fg_splash)
        self.add(self.__label)
        self.__label.set_alignment(self.__label.RIGHT)


    def __on_tab_selected(self, px, py, idx):

        if (self.__lock.isSet()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (idx != self.__index):            
            icon = self.__icons[self.__index]
            img1, img2 = self.__images[self.__index]
            icon.set_image(img1)

            icon = self.__icons[idx]
            img1, img2 = self.__images[idx]
            icon.set_image(img2)

            self.__index = idx
                  
            self.render_at(TEMPORARY_PIXMAP, x, y)
            screen.copy_pixmap(TEMPORARY_PIXMAP, x, y, x, y, w, h)
        
        self.update_observer(self.OBS_TAB_SELECTED, idx)


    def add_viewer(self, v):
    
        x, y = self.__pos        

        if (len(self.__icons) == self.__index):
            pbuf = v.ICON_ACTIVE
        else:
            pbuf = v.ICON

        icon = Image(self.__esens, pbuf)
        #icon.set_size(120, 120)
        self.add(icon)
        icon.connect(icon.EVENT_BUTTON_PRESS, self.__on_tab_selected,
                     len(self.__icons))
        self.__icons.append(icon)
        self.__images.append((v.ICON, v.ICON_ACTIVE))
        
        offx = (128 - v.ICON.get_width()) / 2
        offy = (128 - v.ICON.get_height()) / 2
        icon.set_pos(10 + x * 128 + offx, 10 + y * 128 + offy)

        height = (y + 1) * 130 + 20
        self.set_geometry(0, 480 - height, 800, height)
        self.__label.set_geometry(0, height - 16, 790, 0)

        x += 1
        if (x == 6):
            x = 0
            y += 1
        self.__pos = (x, y)
                    


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
       
        screen.fill_area(x, y, w, h, theme.color_bg)
        #screen.draw_frame(theme.tab_panel, x, y, w, h, True)
        #screen.draw_subpixbuf(theme.background, 0, 0, x, y, w, h)



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
        while (wait and not finished.isSet()): gtk.main_iteration()        
        self.set_events_blocked(False)


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
        while (wait and not finished.isSet()): gtk.main_iteration()        
        self.set_events_blocked(False)
