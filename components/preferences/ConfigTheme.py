from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ThemeListItem import ThemeListItem
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
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        title = LabelItem("Select a Theme:")
        self.__list.append_item(title)
                  
        self.__update_list()
        
        
    def set_size(self, w, h):
    
        Configurator.set_size(self, w, h)
        for item in self.__list.get_items():
            item.set_size(w, 80)


    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)
        
        
    def __on_item_clicked(self, preview, name, title):
    
        gobject.idle_add(self.__change_theme, name, title, preview)


    def __update_list(self):
    
        w, h = self.get_size()
        themes = theme.list_themes()
        self.__themes = []
        for name, preview, title, description, author in themes:
            try:
                img = gtk.gdk.pixbuf_new_from_file(preview)
            except:
                continue
                
            item = ThemeListItem(img, title, description, author)
            item.set_size(w, 80)
            item.connect_clicked(self.__on_item_clicked, preview, name, title)
            
            idx = self.__list.append_item(item)
            self.__themes.append((name, title))
            
            #if (name == config.theme()):
            #    self.__list.hilight(idx)
        #end for


    def __change_theme(self, t, title, preview):

        #self.emit_event(msgs.UI_ACT_SHOW_MESSAGE, "Loading Theme",
        #                "- %s -" % title, preview)
        import time; time.sleep(0.5)
                        
        config.set_theme(t)
        theme.set_theme(t)

        #self.emit_event(msgs.UI_ACT_HIDE_MESSAGE)
        self.emit_event(msgs.CORE_EV_THEME_CHANGED)

