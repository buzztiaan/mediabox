from com import Configurator, msgs
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from ThemeListItem import ThemeListItem
from mediabox.ThrobberDialog import ThrobberDialog
from mediabox import config
import theme

import gtk


class ConfigTheme(Configurator):

    ICON = theme.prefs_theme
    TITLE = "Themes"
    

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ItemList(80)
        self.__list.set_caps(theme.list_top, theme.list_bottom)
        self.__list.set_bg_color(theme.color_bg)
        self.__list.set_scrollbar(theme.list_scrollbar)        
        self.__list.set_geometry(0, 0, 610, 370)
        self.add(self.__list)
            
        kscr = KineticScroller(self.__list)
        kscr.set_touch_area(0, 520)
        kscr.add_observer(self.__on_observe_list)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_text("Loading Theme")
        self.add(self.__throbber)
        self.__throbber.set_visible(False)
        
        self.__update_list()
        

    def __update_list(self):
    
        themes = theme.list_themes()
        self.__themes = []
        for name, preview, title, description in themes:
            img = gtk.gdk.pixbuf_new_from_file(preview)
            item = ThemeListItem(610, 80, img, title + "\n" + description)
            idx = self.__list.append_item(item)
            self.__themes.append(name)
            
            if (name == config.theme()):
                self.__list.hilight(idx)
        

    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)
            if (px >= 540 and idx >= 0):
                self.__list.hilight(idx)
                config.set_theme(self.__themes[idx])
                self.__throbber.set_visible(True)
                self.__throbber.render()
                self.__throbber.rotate()
                theme.set_theme(self.__themes[idx])
                self.__throbber.set_visible(False)
                self.emit_event(msgs.CORE_EV_THEME_CHANGED)

