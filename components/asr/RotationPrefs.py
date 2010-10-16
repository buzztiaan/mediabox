from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import CheckBoxItem
from ui.itemview import OptionItem
from mediabox import config
from utils import logging
import platforms
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
    
        self.__have_unapplied_changes = False
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        #lbl = LabelItem("Orientation:")
        #self.__list.append_item(lbl)
        
        if (platforms.MAEMO5):
            chbox = OptionItem("Landscape Mode", config.ORIENTATION_LANDSCAPE,
                               "Portrait Mode", config.ORIENTATION_PORTRAIT,
                               "Automatic", config.ORIENTATION_AUTOMATIC)
        else:
            chbox = OptionItem("Landscape Mode", config.ORIENTATION_LANDSCAPE,
                               "Portrait Mode", config.ORIENTATION_PORTRAIT)
        
        chbox.connect_changed(self.__on_select_orientation)
        chbox.select_by_value(config.orientation())
        self.__list.append_item(chbox)

        # abusing empty label for space... TODO: implement space item :)
        #lbl = LabelItem("")
        #self.__list.append_item(lbl)

        chk = CheckBoxItem("Swap volume/zoom keys in portrait mode",
                           config.portrait_swap_volume())
        chk.connect_checked(self.__on_check_swap)
        self.__list.append_item(chk)


    def _visibility_changed(self):

        Configurator._visibility_changed(self)
    
        if (not self.is_visible() and self.__have_unapplied_changes):
            self.__have_unapplied_changed = False
            
            orientation = config.orientation()
            self.__set_orientation(orientation)


    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)


    def __on_select_orientation(self, value):
    
        self.__have_unapplied_changes = True

        self.__list.invalidate()
        self.__list.render()

        config.set_orientation(value)
        

    def __set_orientation(self, value):
    
        if (value == config.ORIENTATION_LANDSCAPE):
            self.emit_message(msgs.ASR_ACT_ENABLE, False)
            self.emit_message(msgs.ASR_EV_LANDSCAPE)
            logging.info("[rotation] landscape orientation")

        elif (value == config.ORIENTATION_PORTRAIT):
            self.emit_message(msgs.ASR_ACT_ENABLE, False)
            self.emit_message(msgs.ASR_EV_PORTRAIT)
            logging.info("[rotation] portrait orientation")

        else:
            self.emit_message(msgs.ASR_ACT_ENABLE, True)
            self.emit_message(msgs.ASR_EV_LANDSCAPE)
            logging.info("[rotation] automatic orientation")


    def __on_check_swap(self, v):
    
        config.set_portrait_swap_volume(v)
        self.__list.invalidate()
        self.__list.render()


    def __restore_orientation(self):

        o = config.orientation()
        self.__set_orientation(o)
        #if (o == config.ORIENTATION_PORTRAIT):
        #    self.emit_message(msgs.ASR_EV_PORTRAIT)
        #elif (o == config.ORIENTATION_AUTOMATIC):
        #    self.emit_message(msgs.ASR_ACT_ENABLE, True)
        #    self.emit_message(msgs.ASR_EV_LANDSCAPE)
            

    def handle_COM_EV_APP_STARTED(self):
    
        self.__restore_orientation()


    def handle_ASR_ACT_RESTORE(self):
    
        self.__restore_orientation()

