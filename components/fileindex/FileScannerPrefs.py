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
            if (platforms.MAEMO4): tracker = "Metalayer Crawler"
            elif (platforms.MAEMO5): tracker = "Tracker"
            lbl = LabelItem("Your device provides a tracker service (%s) for "
                            "discovering new media. MediaBox can use it for "
                            "scanning for new media." % tracker)
            self.__list.append_item(lbl)

            btn = ButtonItem("Look for new media now")
            btn.connect_clicked(self.__on_click_update)
            self.__list.append_item(btn)
    
            chk = CheckBoxItem("Look for new media at startup (recommended)",
                               mb_config.scan_at_startup())
            chk.connect_checked(self.__on_check_startup)
            self.__list.append_item(chk)        

        else:
            lbl = LabelItem("Your device does not provide a tracker service for "
                            "discovering new media automatically. You can " \
                            "scan for new media manually by selecting " \
                            "'Scan for Media' from the item popup menu of a "\
                            "local folder.")
            self.__list.append_item(lbl)

            lbl = LabelItem("")
            self.__list.append_item(lbl)
        #end if


        lbl = LabelItem("By clearing the index, MediaBox forgets about all "
                        "media files until you have it scan for media again.")
        self.__list.append_item(lbl)

        btn = ButtonItem("Clear index now")
        btn.connect_clicked(self.__on_click_clear)
        self.__list.append_item(btn)


        lbl = LabelItem("At startup, MediaBox removes media that no longer "
                        "exists from the index. If necessary, you can trigger " \
                        "this manually anytime, too")
        self.__list.append_item(lbl)

        btn = ButtonItem("Remove dead entries from index")
        btn.connect_clicked(self.__on_click_bury)
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


    def __on_click_bury(self):
    
        self.emit_message(msgs.UI_ACT_SHOW_INFO,
                          "Removing dead entries from index.")
        self.emit_message(msgs.FILEINDEX_SVC_BURY)

