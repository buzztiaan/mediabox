from Panel import Panel
from ui.ImageButton import ImageButton
import panel_actions
import theme

import gtk


class MenuPanel(Panel):

    def __init__(self):
    
        self.__current_tab = None
        self.__tabs = []
    
        Panel.__init__(self)
        
        self.__tabbox = gtk.HBox(spacing = 12)
        self.__tabbox.show()
        self.box.pack_start(self.__tabbox, False, False)
        
        
    def add_tab(self, icon, name):
        """
        Adds a new menu tab.
        """

        # this is a gtk.Layout instead of a gtk.Fixed because we want to be
        # able to catch button events
        tab = gtk.Layout()
        tab.set_size_request(80, 80)
        tab.connect("button-press-event", self.__on_select_tab, name)
        tab.show()
        
        bg = gtk.Image()
        bg.set_from_pixbuf(theme.panel_bg)
        bg.show()
        tab.put(bg, 0, 0)
        
        tab.hilight = gtk.Image()
        tab.hilight.set_from_pixbuf(theme.active_tab)
        tab.put(tab.hilight,
                40 - theme.active_tab.get_width() / 2,
                40 - theme.active_tab.get_height() / 2)
        
        img = gtk.Image()
        img.set_from_pixbuf(icon)
        img.show()
        tab.put(img,
                40 - icon.get_width() / 2,
                40 - icon.get_height() / 2)
                
        self.__tabbox.pack_start(tab, False, False)
        self.__tabs.append((tab, name))


    def __on_select_tab(self, src, event, name):
    
        cnt = 0
        for t, n in self.__tabs:
            if (t == src and t != self.__current_tab):
                self.select_tab(cnt)
                break
            cnt += 1
        #end for
        
        

    def select_tab(self, idx):
        
        if (self.__current_tab):
            self.__current_tab.hilight.hide()
            
        self.__current_tab, name = self.__tabs[idx]
        self.__current_tab.hilight.show()
        self.update_observer(panel_actions.TAB_SELECTED, name)
        
