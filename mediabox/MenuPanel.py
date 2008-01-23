from Panel import Panel
from ui.TabsBar import TabsBar
import panel_actions


class MenuPanel(Panel):

    def __init__(self, esens):
    
        self.__current_tab = None
    
        Panel.__init__(self, esens)
        self.__tabsbar = TabsBar(esens)
        self.add(self.__tabsbar)
        
        
    def add_tab(self, icon, icon_active, name):
        """
        Adds a new menu tab.
        """
        
        self.__tabsbar.add_tab(icon, icon_active,
                               lambda n:self.update_observer(panel_actions.TAB_SELECTED, n),
                               name)
        w, h = self.get_size()
        tabs_w, tabs_h = self.__tabsbar.get_size()
        tabs_x = w - tabs_w                               
        self.__tabsbar.set_pos(tabs_x, 0)      


    def select_tab(self, idx):

        self.__tabsbar.hilight_tab(idx)        
        
