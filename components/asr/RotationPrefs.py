from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import CheckBoxItem
from ui.itemview import OptionItem
from mediabox import config
from theme import theme

import os



class RotationPrefs(Configurator):
    """
    Configurator for display rotation.
    """

    ICON = theme.prefs_icon_asr
    TITLE = "Display Orientation"
    DESCRIPTION = "Configure the display orientation"


    def __init__(self):
    
        self.__is_portrait = False
        
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        #lbl = LabelItem("Orientation:")
        #self.__list.append_item(lbl)
        
        chbox = OptionItem("Landscape Mode", config.ORIENTATION_LANDSCAPE,
                           "Portrait Mode", config.ORIENTATION_PORTRAIT)
        chbox.connect_changed(self.__on_select_orientation)
        chbox.select_by_value(config.orientation())
        self.__list.append_item(chbox)

        # abusing empty label for space... TODO: implement space item :)
        lbl = LabelItem("")
        self.__list.append_item(lbl)

        chk = CheckBoxItem("Swap volume/zoom keys in portrait mode",
                           config.portrait_swap_volume())
        chk.connect_checked(self.__on_check_swap)
        self.__list.append_item(chk)


    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)


    def __on_select_orientation(self, value):

        self.__list.invalidate()
        self.__list.render()
    
        if (value == config.ORIENTATION_LANDSCAPE):
            self.emit_message(msgs.ASR_EV_LANDSCAPE)
            self.__is_portrait = False
        else:
            self.emit_message(msgs.ASR_EV_PORTRAIT)
            self.__is_portrait == True
        config.set_orientation(value)


    def __on_check_swap(self, v):
    
        config.set_portrait_swap_volume(v)
        self.__list.invalidate()
        self.__list.render()


    def handle_COM_EV_APP_STARTED(self):
    
        o = config.orientation()
        if (o == config.ORIENTATION_PORTRAIT):
            self.emit_message(msgs.ASR_EV_PORTRAIT)


    def handle_ASR_EV_PORTRAIT(self):
    
        self.__is_portrait = True


    def handle_ASR_EV_LANDSCAPE(self):
    
        self.__is_portrait = False


    def handle_ASR_ACT_FORCE_LANDSCAPE(self, value):
    
        if (value):
            self.emit_message(msgs.ASR_EV_LANDSCAPE)
        else:
            if (self.__is_portrait):
                self.emit_message(msgs.ASR_EV_PORTRAIT)

