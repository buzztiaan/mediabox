from com import Configurator, msgs
from ui.Label import Label
from ui.CheckBox import CheckBox
from ui.RadioGroup import RadioGroup
from ui.VBox import VBox
import config
import theme

import os


class Prefs(Configurator):

    ICON = theme.fmradio_viewer_radio
    TITLE = "FM Radio"

    def __init__(self):
    
        Configurator.__init__(self)
        
        vbox = VBox()
        vbox.set_geometry(0, 0, 620, 370)
        self.add(vbox)
        
        lbl = Label("FM radio region:\n",
                    theme.font_plain, theme.color_fg_item)
        vbox.add(lbl)

        buttons = []
        for option, value in [("US/Europe (used in most parts of the world)\n", "EUR"),
                              ("Japan (requires a custom kernel)\n", "JPN")]:
            chkbox = CheckBox(value == config.get_region())
            chkbox.connect_checked(self.__on_select_fm_band, value)
            vbox.add(chkbox)
        
            lbl = Label(option, theme.font_plain, theme.color_fg_item_2)
            chkbox.add(lbl)
            
            buttons.append(chkbox)
        #end for
        
        grp = RadioGroup(*buttons)

        lbl = Label("Depending on the laws in your country,\n"
                    "operating a FM radio with an inappropriate\n"
                    "region setting may be illegal.",
                    theme.font_plain, theme.color_fg_item)
        vbox.add(lbl)




    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x, y, w, h, theme.color_bg)
        
        
    def __on_select_fm_band(self, is_checked, value):
    
        if (is_checked):
            config.set_region(value)

