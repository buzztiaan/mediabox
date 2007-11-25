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


class ControlBar(gtk.HBox, Observable):    

    def __init__(self):
    
        self.__panels = []
        self.__current_panel = 0
        
    
        gtk.HBox.__init__(self)
        self.set_size_request(800, 80)       

        self.__menu_panel = MenuPanel()
        self.__menu_panel.show()
        self.__add_panel(self.__menu_panel)
        
        self.__control_panel = ControlPanel()
        self.__add_panel(self.__control_panel)
        
        self.__volume_panel = VolumePanel()
        self.__add_panel(self.__volume_panel)

        self.__progress_panel = ProgressPanel()
        self.__add_panel(self.__progress_panel)
        
        self.__message_panel = MessagePanel()
        self.__add_panel(self.__message_panel)
        
        
    def __add_panel(self, panel):
    
        panel.add_observer(self.__on_observe_panels)
        self.add(panel)
        if (panel.has_next_button()):
            self.__panels.append(panel)


    def __on_observe_panels(self, src, cmd, *args):
    
        if (cmd == src.OBS_NEXT_PANEL):
            self.next_panel()
        
        else:
            self.update_observer(cmd, *args)
       

    def set_capabilities(self, capabilities):
        """
        Tells the control panel about the current viewer's capabilities.
        """
    
        self.__control_panel.set_capabilities(capabilities)
            


    def next_panel(self):
        """
        Switches to the next panel.
        """
            
        panel1 = self.__panels[self.__current_panel]
        idx = (self.__current_panel + 1) % len(self.__panels)
        panel2 = self.__panels[idx]
        panel1.hide()
        panel2.show()
        self.__current_panel = idx
        
        
    def __show_panel_with_timeout(self, panel, timeout):
        """
        Displays the given panel for a given amount of time.
        """
    
        self.__panels[self.__current_panel].hide()
        panel.show()
        
        # what a dirty hack... but it works well
        panel.timeout_ticket = `time.time()`
        
        def f(timeout_ticket):
            if (timeout_ticket == panel.timeout_ticket):
                panel.hide()    
                self.__panels[self.__current_panel].show()
            
        gobject.timeout_add(timeout, f, panel.timeout_ticket)


    def add_tab(self, icon, name):
        """
        Adds a new viewer tab to the menu panel.
        """
    
        self.__menu_panel.add_tab(icon, name)
        
        
    def select_tab(self, idx):
        """
        Selects the given viewer tab.
        """
    
        self.__menu_panel.select_tab(idx)
        
        
    def set_playing(self, value):
            
        self.__control_panel.set_playing(value)
        
        
    def set_position(self, pos, total):
    
        self.__control_panel.set_position(pos, total)


    def set_title(self, title):

        self.__control_panel.set_title(title)    


    def set_volume(self, percent):
    
        self.__volume_panel.set_volume(percent)
        self.__show_panel_with_timeout(self.__volume_panel, 500)


    def set_progress(self, value, total):
    
        self.__progress_panel.set_progress(value, total)
        self.__show_panel_with_timeout(self.__progress_panel, 500)


    def show_message(self, message):
    
        self.__message_panel.set_message(message)
        self.__panels[self.__current_panel].hide()
        self.__message_panel.show()
        
        
    def show_panel(self):
    
        self.__message_panel.hide()
        self.__panels[self.__current_panel].show()
        
