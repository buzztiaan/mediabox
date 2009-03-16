from com import Configurator, msgs
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
from ui.CheckBox import CheckBox
from ui.VBox import VBox
from utils import mmc
import config
from theme import theme

import os


class Prefs(Configurator):

    ICON = theme.youtube_device
    TITLE = "YouTube"
    DESCRIPTION = "Configure the YouTube plugin"


    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)
        
        lbl = Label("Save YouTube videos to:",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        current_cache = config.get_cache_folder()
        chbox = ChoiceBox("device", os.path.expanduser("~"),
                          mmc.get_label("/media/mmc2"), "/media/mmc2",
                          mmc.get_label("/media/mmc1"), "/media/mmc1")
        chbox.select_by_value(current_cache)
        chbox.connect_changed(self.__on_select_cache_location)
        self.__vbox.add(chbox)

        chk = CheckBox(config.get_hi_quality())
        chk.connect_checked(self.__on_check_hi_quality)
        self.__vbox.add(chk)
        lbl = Label("Retrieve high-quality version of video if available\n"
                    "(HQ videos don't play well on the Nokia N8x0 devices)",
                    theme.font_mb_plain, theme.color_mb_listitem_text)        
        chk.add(lbl)
        



    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_select_cache_location(self, location):
    
        config.set_cache_folder(location)


    def __on_check_hi_quality(self, v):
    
        config.set_hi_quality(v)

