from PrefsCard import PrefsCard
from ui.Item import Item
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from ui import dialogs
from mediabox import config
import theme

import gtk


class CardThemeSelector(PrefsCard):

    def __init__(self, esens, title):        
    
        self.__themes = []
        
    
        PrefsCard.__init__(self, esens, title)

        self.__list = ItemList(esens, 600, 80)
        self.__list.set_background(theme.background.subpixbuf(185, 32, 600, 368))
        self.__list.set_graphics(theme.item, theme.item_active)
        self.__list.set_font(theme.font_plain)
        self.__list.set_arrows(theme.arrows)
        self.__list.set_pos(10, 0)
        self.__list.set_size(600, 350)
        self.add(self.__list)
            
        kscr = KineticScroller(self.__list)
        kscr.add_observer(self.__on_observe_list)
        
        self.__update_list()
        
        
    def __update_list(self):
    
        themes = theme.list_themes()
        self.__themes = []
        for name, preview, title, description in themes:
            img = gtk.gdk.pixbuf_new_from_file(preview)
            idx = self.__list.append_item(title + "\n" + description, img)
            self.__list.overlay_image(idx, theme.btn_load, 540, 16)
            self.__themes.append(name)
            
            if (name == config.theme()):
                self.__list.hilight(idx)
        

    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)
            
            if (px > 520 and idx >= 0):
                self.__list.hilight(idx)
                config.set_theme(self.__themes[idx])
                dialogs.info("Information",
                             "Theme will change after restarting.")
