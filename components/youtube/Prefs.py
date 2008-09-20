from com import Configurator, msgs
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
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
        chbox = ChoiceBox("device", os.path.expanduser("~"),
                          "internal memory card", "/media/mmc2",
                          "external memory card", "/media/mmc1")
        chbox.select_by_value(current_cache)
        chbox.connect_changed(self.__on_select_cache_location)
        vbox.add(chbox)
        



    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_bg)
        
        
    def __on_select_cache_location(self, location):
    
        config.set_cache_folder(location)

