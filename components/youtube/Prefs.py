from com import Configurator, msgs
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
from ui.VBox import VBox
from utils import mmc
import config
from theme import theme

import os


class Prefs(Configurator):

    ICON = theme.youtube_device
    TITLE = "YouTube"

    def __init__(self):
    
        Configurator.__init__(self)
        
        vbox = VBox()
        vbox.set_geometry(0, 0, 620, 370)
        self.add(vbox)
        
        lbl = Label("Save YouTube videos to:\n",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        vbox.add(lbl)

        current_cache = config.get_cache_folder()
        chbox = ChoiceBox("device", os.path.expanduser("~"),
                          mmc.get_label("/media/mmc2"), "/media/mmc2",
                          mmc.get_label("/media/mmc1"), "/media/mmc1")
        chbox.select_by_value(current_cache)
        chbox.connect_changed(self.__on_select_cache_location)
        vbox.add(chbox)
        



    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_select_cache_location(self, location):
    
        config.set_cache_folder(location)

