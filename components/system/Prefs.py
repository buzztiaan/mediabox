from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import OptionItem
from theme import theme
import config

import os


_DESCRIPTIONS = {"no":
                 "The display switches off normally when the device goes into\n"
                 "powersaving.",
                 "yes":
                 "The display does not switch off and the device does not go\n"
                 "into powersaving, unless the menu panel is open.",
                 "playing":
                 "The display does not switch off while playing media.",
                 "ac":
                 "The display doesn't turn off when the device is powered by\n"
                 "powered by the AC adapter."}


class Prefs(Configurator):

    ICON = theme.mb_device_n800
    TITLE = "Device"
    DESCRIPTION = "Configure the device hardware"


    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.__list.set_background(theme.color_mb_background)
        self.add(self.__list)
        
        lbl = LabelItem("Keep display lit:")
        self.__list.append_item(lbl)
        
        chbox = OptionItem("never", "no",
                           "while playing", "playing",
                           "yes", "yes")
        chbox.connect_changed(self.__on_select_display_lit)
        self.__list.append_item(chbox)
        

    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)
        
        
    def __on_select_display_lit(self, value):
    
        self.__list.invalidate()
        self.__list.render()
        config.set_display_lit(value)
        self.__label_lit.set_text(_DESCRIPTIONS[value])

