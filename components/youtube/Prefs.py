from com import Configurator, msgs
from ui.Label import Label
from ui.CheckBox import CheckBox
from ui.RadioGroup import RadioGroup
from ui.VBox import VBox
import config
import theme

import os


class Prefs(Configurator):

    ICON = theme.youtube_device
    TITLE = "YouTube"

    def __init__(self):
    
        Configurator.__init__(self)
        
        vbox = VBox()
        vbox.set_geometry(0, 0, 620, 370)
        self.add(vbox)
        
        lbl = Label("Please specify where you want MediaBox to cache\n"
                    "YouTube videos for playing:\n",
                    theme.font_plain, theme.color_fg_item)
        vbox.add(lbl)

        current_cache = config.get_cache_folder()
        buttons = []
        for option, location in [("on the device\n", os.path.expanduser("~")),
                       ("on the internal memory card\n", "/media/mmc2"),
                       ("on the external memory card\n", "/media/mmc1")]:        
            chkbox = CheckBox(current_cache == location)
            chkbox.connect_checked(self.__on_select_cache_location, location)
            vbox.add(chkbox)
        
            lbl = Label(option, theme.font_plain, theme.color_fg_item_2)
            chkbox.add(lbl)
            
            buttons.append(chkbox)
        #end for
        
        grp = RadioGroup(*buttons)




    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_bg)
        
        
    def __on_select_cache_location(self, is_checked, location):
    
        if (is_checked):
            config.set_cache_folder(location)

