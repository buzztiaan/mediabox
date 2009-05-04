from com import Viewer, msgs
from ui.SideTabs import SideTabs
from utils import logging
from theme import theme

import gobject


class TabbedViewer(Viewer):
    """
    Base class for a viewer with tabs.

    @since: 0.96.5
    """

    def __init__(self):
    
        # the currently visible tab element
        self.__current_tab_element = None


        Viewer.__init__(self)
        
        # side tabs
        self.__side_tabs = SideTabs()
        self.add(self.__side_tabs)

        
    def add_tab(self, name, element, cb, *args):
        """
        Adds a new tab with the given name for the given view mode.
        """    

        def f():
            if (self.__current_tab_element):
                self.__current_tab_element.set_visible(False)
            element.set_visible(True)
            self.__current_tab_element = element

            if (cb):
                cb(*args)

            self.render()
            

        self.__side_tabs.add_tab(None, name, f)


    def select_tab(self, idx):
        """
        Selects the given tab.
        """
        
        self.__side_tabs.select_tab(idx)


    def switch_tab(self):
        """
        Switches tabs.
        @since: 0.96.5
        """
    
        self.__side_tabs.switch_tab()
        

    def set_tabs_visible(self, v):
    
        self.__side_tabs.set_visible(v)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
               
        if (self.__side_tabs.is_visible()):
            self.__side_tabs.set_geometry(w - 66, 4, 66, h - 8)
            if (self.__current_tab_element):
                self.__current_tab_element.set_geometry(0, 0, w - 70, h)
        else:
            if (self.__current_tab_element):
                self.__current_tab_element.set_geometry(0, 0, w, h)
       
        #screen.fill_area(x, y, w, h, theme.color_mb_background)
        

    def show(self):
    
        Viewer.show(self)
        
        if (not self.__current_tab_element):
            self.select_tab(0)

