from com import Configurator, msgs
from ui.ItemList import ItemList
from ThemeListItem import ThemeListItem
from mediabox.TrackList import TrackList
from mediabox import config
import theme

import gtk
import gobject


class ConfigTheme(Configurator):

    ICON = theme.prefs_theme
    TITLE = "Themes"
    

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = TrackList()
        self.__list.set_geometry(0, 0, 610, 370)
        self.__list.connect_button_clicked(self.__on_item_button)
        self.add(self.__list)
                  
        self.__update_list()
        
        
    def __on_item_button(self, item, idx, btn):
    
        self.__list.hilight(idx)
        self.render()
        theme = self.__themes[idx]
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                          "Loading theme %s..." % theme)
        gobject.idle_add(self.__change_theme, theme)



    def __update_list(self):
    
        themes = theme.list_themes()
        self.__themes = []
        for name, preview, title, description in themes:
            img = gtk.gdk.pixbuf_new_from_file(preview)
            item = ThemeListItem(img, title, description)
            idx = self.__list.append_item(item)
            self.__themes.append(name)
            
            if (name == config.theme()):
                self.__list.hilight(idx)


    def __change_theme(self, t):

        config.set_theme(t)
        theme.set_theme(t)
        self.emit_event(msgs.CORE_EV_THEME_CHANGED)

