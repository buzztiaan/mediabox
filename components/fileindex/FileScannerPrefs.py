from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import ButtonItem
from ui.itemview import CheckBoxItem
from ui.itemview import LabelItem
from theme import theme
from mediabox import config as mb_config

import time


class FileScannerPrefs(Configurator):
    """
    Configurator for file indexing.
    """

    ICON = theme.prefs_icon_fileindex
    TITLE = "Media Indexing"
    DESCRIPTION = "Configure file indexing"
    

    def __init__(self):
    
        Configurator.__init__(self)

        self.__list = ThumbableGridView()
        self.add(self.__list)


        chk = CheckBoxItem("Always update index at startup (recommended)",
                           mb_config.scan_at_startup())
        chk.connect_checked(self.__on_check_startup)
        self.__list.append_item(chk)

        btn = ButtonItem("Update index now")
        btn.connect_clicked(self.__on_click_update)
        self.__list.append_item(btn)

        lbl = LabelItem("If you prefer to browse the filesystem directly, you "
                        "may clear the index and disable automatic updating "
                        "of the index at startup.")
        self.__list.append_item(lbl)

        btn = ButtonItem("Clear index now")
        btn.connect_clicked(self.__on_click_clear)
        self.__list.append_item(btn)
        
        
    def __on_check_startup(self, value):
    
        mb_config.set_scan_at_startup(value)
        self.__list.invalidate()
        self.__list.render()


    def __on_click_update(self):
    
        self.emit_message(msgs.UI_ACT_SHOW_INFO, "Updating media index.")
        self.emit_message(msgs.FILEINDEX_ACT_SCAN)


    def __on_click_clear(self):
    
        self.emit_message(msgs.UI_ACT_SHOW_INFO, "Clearing media index.")
        self.emit_message(msgs.FILEINDEX_SVC_CLEAR)

