from PrefsCard import PrefsCard
from ui.Item import Item
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from mediabox import config
import theme

import gtk


class CardThemeSelector(PrefsCard):

    def __init__(self, title):        
    
        PrefsCard.__init__(self, title)
    
        self.__list = ItemList(600, 80)
        self.__list.set_background(theme.background.subpixbuf(185, 32, 600, 368))
        self.__list.set_graphics(theme.item, theme.item_active)
        self.__list.set_font(theme.font_plain)
        self.__list.set_arrows(theme.arrows)                
        self.__list.show()
            
        kscr = KineticScroller(self.__list)
        kscr.add_observer(self.__on_observe_list)
        kscr.show()
        self.pack_start(kscr, True, True, 12)
        
        self.__update_list()
        self.__list.hilight(0)
        
        
    def __update_list(self):
    
        themes = theme.list_themes()
        for name, preview in themes:
            img = gtk.gdk.pixbuf_new_from_file(preview)
            self.__list.append_item(name, img)
        

    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)
            
            if (px > 520 and idx >= 0):
                self.__list.hilight(idx)
                
