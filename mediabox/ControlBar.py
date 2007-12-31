from ui.Pixmap import Pixmap
from ui.Widget import Widget

from utils.Observable import Observable
from MenuPanel import MenuPanel
from ControlPanel import ControlPanel
from VolumePanel import VolumePanel
from ProgressPanel import ProgressPanel
from MessagePanel import MessagePanel
import panel_actions
import theme

import gtk
import gobject
import time
import threading



class ControlBar(Widget, Observable):

    def __init__(self, esens):
        
        self.__panels = []
        self.__current_panel = 0
    
        Widget.__init__(self, esens)
        self.set_size(800, 80)

        self.__menu_panel = MenuPanel(esens)
        self.__add_panel(self.__menu_panel)

        self.__control_panel = ControlPanel(esens)
        self.__add_panel(self.__control_panel)

        self.__volume_panel = VolumePanel(esens)
        self.__volume_panel.set_visible(False)        
        self.add(self.__volume_panel)

        self.__message_panel = MessagePanel(esens)
        self.__message_panel.set_visible(False)
        self.add(self.__message_panel)

        #self.__add_panel(self.__volume_panel)
          
        
    def __add_panel(self, panel):
    
        panel.set_visible(False)
        self.add(panel)
        panel.add_observer(self.__on_observe_panel)
        self.__panels.append(panel)
        
        
        
    def __on_observe_panel(self, src, cmd, *args):
    
        if (cmd == src.OBS_NEXT_PANEL):
            self.next_panel()
        else:
            self.update_observer(cmd, *args)
                          
        
    def fx_raise(self, wait = True):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)       
        panel = self.__panels[self.__current_panel]
        panel.set_visible(True)
        panel.render_at(buf)
        finished = threading.Event()
        
        def fx(i):
            screen.copy_pixmap(buf, 0, 0, x, y + h - i, w, i)
            if (i < 80):
                gobject.timeout_add(5, fx, i + 4)
            else:
                finished.set()

        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration()


    def fx_lower(self, wait = True):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__panels[self.__current_panel].set_visible(False)
        finished = threading.Event()
        
        def fx(i):
            screen.copy_pixmap(screen, x, y + i, x, y + i + 4, w, h - i)
            screen.draw_subpixbuf(theme.background, x, y + i, x, y + i, w, 4)
            if (i < 80):
                gobject.timeout_add(5, fx, i + 4)
            else:
                finished.set()
                
        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration()
        

    def fx_slide_in(self, panel = None, wait = True):

        if (not panel):
            panel = self.__panels[self.__current_panel]

        STEP = 50
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        panel.render_at(buf)
        finished = threading.Event()
        panel.set_frozen(True)

        def fx(i):        
            screen.copy_pixmap(screen, 100 + STEP, y, 100, y, w - 100 - STEP, h)
            screen.copy_pixmap(buf, 100 + i, 0, w - STEP, y, STEP, h)
            if (i < 700 - STEP):
                gobject.timeout_add(5, fx, i + STEP)
            else:
                panel.set_frozen(False)
                finished.set()

        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration()


    def fx_slide_out(self, wait = True):
    
        STEP = 50
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        finished = threading.Event()
    
        panel = self.__panels[self.__current_panel]
        panel.set_frozen(True)
    
        def fx(i):
            screen.copy_pixmap(screen, 100, y, 100 + STEP, y, w - 100 - STEP, h)
            screen.draw_subpixbuf(theme.panel, 100, 0, 100 + i, y, STEP, h)
            if (i < 700 - STEP):
                gobject.timeout_add(5, fx, i + STEP)
            else:
                panel.set_frozen(False)
                finished.set()
        
        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration()
        


    def next_panel(self):
        """
        Switches to the next panel.
        """
        
        panel1 = self.__panels[self.__current_panel]
        idx = (self.__current_panel + 1) % len(self.__panels)
        panel2 = self.__panels[idx]

        panel1.set_visible(False)
        panel2.set_visible(True)

        self.__current_panel = idx
        self.switch_to_panel(panel2)


    def __show_panel_with_timeout(self, panel, timeout):
        """
        Displays the given panel for a given amount of time.
        """
    
        if (not self.may_render()): return
    
        self.__panels[self.__current_panel].set_visible(False)
        panel.set_visible(True)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)
        panel.render_at(buf)
        screen.copy_pixmap(buf, 0, 0, x, y, w, h)
        
        # what a dirty hack... but it works well
        panel.timeout_ticket = `time.time()`
        
        def f(timeout_ticket):
            if (timeout_ticket == panel.timeout_ticket):
                panel.set_visible(False)
                self.__panels[self.__current_panel].set_visible(True)
                self.__panels[self.__current_panel].render()

        gobject.timeout_add(timeout, f, panel.timeout_ticket)
        

    def add_tab(self, icon, icon_active, name):
        """
        Adds a new viewer tab to the menu panel.
        """
    
        self.__menu_panel.add_tab(icon, icon_active, name)
        
        
    def select_tab(self, i):

        self.__menu_panel.select_tab(i)    
        self.update_observer(panel_actions.TAB_SELECTED, i)

    
    def set_title(self, title):

        self.__control_panel.set_title(title)        

    
    def set_capabilities(self, caps):
        """
        Tells the control panel about the current viewer's capabilities.
        """
    
        self.__control_panel.set_capabilities(caps)
        
        
    def set_position(self, pos, total):
    
        self.__control_panel.set_position(pos, total)


    def set_progress(self, value, total):
    
        pass
        

    def set_volume(self, percent):
    
        self.__volume_panel.set_volume(percent)
        self.__show_panel_with_timeout(self.__volume_panel, 500)

        
    def set_playing(self, value):
    
        pass
        
        
    def show_panel(self):
    
        panel = self.__panels[self.__current_panel]
        self.__message_panel.set_visible(False)        
        panel.set_visible(True)
        panel.render()
        
        
    def show_message(self, msg):

        self.__message_panel.set_message(msg)
        self.__panels[self.__current_panel].set_visible(False)
        self.__message_panel.set_visible(True)
        self.__message_panel.render()
        
        
    def switch_to_panel(self, panel):
    
        self.render()
        #self.fx_slide_out()
        #self.fx_slide_in(panel)
        
