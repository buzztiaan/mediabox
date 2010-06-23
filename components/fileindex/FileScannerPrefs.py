from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import ButtonItem
from ui.itemview import CheckBoxItem
from ui.itemview import LabelItem
from theme import theme
from mediabox import config as mb_config
import platforms

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

        if (platforms.MAEMO4 or platforms.MAEMO5):
            chk = CheckBoxItem("Look for new media at startup (recommended)",
                               mb_config.scan_at_startup())
            chk.connect_checked(self.__on_check_startup)
            self.__list.append_item(chk)        

            btn = ButtonItem("Look for new media now")
            btn.connect_clicked(self.__on_click_update)
            self.__list.append_item(btn)

        #lbl = LabelItem("You can manually scan folders for new media with the "
        #                "'Scan for Media' option in the popup item menu.")
        #self.__list.append_item(lbl)

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

