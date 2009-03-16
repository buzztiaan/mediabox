from com import Configurator, msgs
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
from ui.VBox import VBox
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
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)
        
        lbl = Label("Keep display lit:",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        lit = config.get_display_lit()
        chbox = ChoiceBox("never", "no",
                          "while playing", "playing",
                          #"when on AC", "ac",
                          "yes", "yes")
        chbox.select_by_value(lit)
        chbox.connect_changed(self.__on_select_display_lit)
        self.__vbox.add(chbox)
      
        self.__label_lit = Label(_DESCRIPTIONS[lit],
                                 theme.font_mb_plain,
                                 theme.color_mb_listitem_text)
        self.__vbox.add(self.__label_lit)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_select_display_lit(self, value):
    
        config.set_display_lit(value)
        self.__label_lit.set_text(_DESCRIPTIONS[value])

