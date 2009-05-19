from com import Configurator, msgs
from ui.ItemList import ItemList
from ThemeListItem import ThemeListItem
from mediabox.TrackList import TrackList
from mediabox import config
from theme import theme

import gtk
import gobject


class ConfigTheme(Configurator):
    """
    Configurator for selecting the UI theme.
    """

    ICON = theme.prefs_theme
    TITLE = "Themes"
    DESCRIPTION = "Change the look of MediaBox with themes"
    

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = TrackList()
        self.__list.connect_button_clicked(self.__on_item_button)
        self.add(self.__list)
                  
        self.__update_list()
        
        
    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)
        
        
    def __on_item_button(self, item, idx, btn):
    
        self.__list.hilight(idx)
        self.render()
        theme, title = self.__themes[idx]
        #self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
        #                  "Loading theme %s..." % theme)
        gobject.idle_add(self.__change_theme, theme, title, item.get_preview())



    def __update_list(self):
    
        themes = theme.list_themes()
        self.__themes = []
        for name, preview, title, description, author in themes:
            try:
                img = gtk.gdk.pixbuf_new_from_file(preview)
            except:
                continue
            item = ThemeListItem(img, title, description, author)
            idx = self.__list.append_item(item)
            self.__themes.append((name, title))
            
            if (name == config.theme()):
                self.__list.hilight(idx)


    def __change_theme(self, t, title, preview):

        self.emit_event(msgs.UI_ACT_SHOW_MESSAGE, "Loading Theme",
                        "- %s -" % title, preview)
        import time; time.sleep(0.5)
                        
        config.set_theme(t)
        theme.set_theme(t)

        self.emit_event(msgs.UI_ACT_HIDE_MESSAGE)
        self.emit_event(msgs.CORE_EV_THEME_CHANGED)

