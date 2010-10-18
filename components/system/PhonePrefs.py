from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import OptionItem
from theme import theme
import config

import os


_DESCRIPTIONS = {config.RESUME_AUTOMATIC:
                 "Media interrupted by a phone call resumes playing after the "
                 "call finished.",
                 config.RESUME_MANUAL:
                 "Media interrupted by a phone call does not resume "
                 "automatically after the call finished."}


class PhonePrefs(Configurator):
    """
    Configurator for setting the phone behavior.
    """

    ICON = theme.prefs_icon_displaylight
    TITLE = "Phone Behavior"
    DESCRIPTION = "Configure the phone behavior"


    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        lbl = LabelItem("Behavior after a phone call:")
        self.__list.append_item(lbl)
        
        chbox = OptionItem("Resume playing", config.RESUME_AUTOMATIC,
                           "Stay paused", config.RESUME_MANUAL)
        chbox.connect_changed(self.__on_select_phonecall_resume)
        self.__list.append_item(chbox)
      
        self.__label_info = LabelItem("")
        self.__list.append_item(self.__label_info)
        chbox.select_by_value(config.get_phonecall_resume())
        
        
    def __on_select_phonecall_resume(self, value):
    
        config.set_phonecall_resume(value)
        self.__label_info.set_text(_DESCRIPTIONS[value])
        self.__list.invalidate()
        self.__list.render()

