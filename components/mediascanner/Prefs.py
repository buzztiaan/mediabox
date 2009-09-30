from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import ButtonItem
from ui.itemview import CheckBoxItem
from ui.itemview import LabelItem
from theme import theme
from mediabox import config as mb_config

import time


class Prefs(Configurator):

    ICON = theme.mediascanner_prefs
    TITLE = "Media Indexing"
    DESCRIPTION = "Configure file indexing and thumbnail previews"
    

    def __init__(self):
    
        Configurator.__init__(self)

        self.__list = ThumbableGridView()
        self.add(self.__list)


        chk = CheckBoxItem("Always update index at startup", False)
        chk.connect_checked(self.__on_check_startup)
        self.__list.append_item(chk)

        btn = ButtonItem("Update index now")
        btn.connect_clicked(self.__on_click_rebuild)
        self.__list.append_item(btn)

        chk = CheckBoxItem("Store thumbnails on the same medium as the " \
                           "associated files", False)
        chk.connect_checked(self.__on_check_store_thumbs)
        self.__list.append_item(chk)

        btn = ButtonItem("Clear preview icons")
        btn.connect_clicked(self.__on_click_reset)
        self.__list.append_item(btn)


    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)        
        
        
    def __on_check_startup(self, value):
    
        mb_config.set_scan_at_startup(value)
        self.__list.invalidate()
        self.__list.render()


    def __on_check_inotify(self, value):
    
        mb_config.set_scan_with_inotify(value)


    def __on_check_store_thumbs(self, value):
    
        mb_config.set_store_thumbnails_on_medium(value)
        self.__list.invalidate()
        self.__list.render()


    def __on_click_reset(self):
    
        mb_config.set_thumbnails_epoch(int(time.time()))


    def __on_click_rebuild(self):
    
        mediaroots = mb_config.mediaroot()
        self.emit_event(msgs.CORE_ACT_SCAN_MEDIA, True)

