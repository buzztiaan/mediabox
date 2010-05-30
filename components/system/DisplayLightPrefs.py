from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import OptionItem
from theme import theme
import config

import os


_DESCRIPTIONS = {"no":
                 "The display switches off normally when the device goes into "
                 "powersaving.",
                 "yes":
                 "The display does not switch off and the device does not go "
                 "into powersaving, unless the menu panel is open.",
                 "playing":
                 "The display does not switch off while playing media.",
                 "ac":
                 "The display doesn't turn off when the device is powered by "
                 "the AC adapter."}


class DisplayLightPrefs(Configurator):
    """
    Configurator for setting the display light behavior.
    """

    ICON = theme.prefs_icon_displaylight
    TITLE = "Display Light"
    DESCRIPTION = "Configure the display light"


    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        lbl = LabelItem("Keep display lit:")
        lbl.set_font(theme.font_mb_headline)
        self.__list.append_item(lbl)
        
        chbox = OptionItem("never", "no",
                           "while playing", "playing")
                           #"yes", "yes")
        chbox.connect_changed(self.__on_select_display_lit)
        self.__list.append_item(chbox)
      
        self.__label_lit = LabelItem("")
        self.__list.append_item(self.__label_lit)
        chbox.select_by_value(config.get_display_lit())
        
        
    def __on_select_display_lit(self, value):
    
        config.set_display_lit(value)
        self.__label_lit.set_text(_DESCRIPTIONS[value])
        self.__list.invalidate()
        self.__list.render()

