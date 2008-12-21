from com import Configurator, msgs
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
from ui.VBox import VBox
import config
from theme import theme

import os


class Prefs(Configurator):

    ICON = theme.fmradio_viewer_radio
    TITLE = "FM Radio"

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        #self.__vbox.set_geometry(0, 0, 620, 370)
        self.add(self.__vbox)
        
        lbl = Label("FM radio region:\n",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        chbox = ChoiceBox("US/Europe", "EUR",
                          "Japan", "JPN")
        chbox.select_by_value(config.get_region())
        chbox.connect_changed(self.__on_select_fm_band)
        self.__vbox.add(chbox)

        lbl = Label("\nDepending on the laws in your country,\n"
                    "operating a FM radio with an inappropriate\n"
                    "region setting may be illegal.",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)




    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_select_fm_band(self, value):

        config.set_region(value)

