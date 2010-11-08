from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.dialog import InfoDialog
from ui import Pixmap
from ThemeListItem import ThemeListItem
from mediabox import config
from theme import theme

import gtk
import gobject
import time


class ConfigTheme(Configurator):
    """
    Configurator for selecting the UI theme.
    """

    ICON = theme.prefs_icon_theme
    TITLE = "Themes"
    DESCRIPTION = "Change the look of MediaBox with themes"
    

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
                         
        self.__update_list()
        
        
    def set_size(self, w, h):
    
        Configurator.set_size(self, w, h)
        for item in self.__list.get_items():
            item.set_size(w, 80)
        
        
    def __on_item_clicked(self, preview, name, title, idx):
    
        self.__list.set_hilight(idx)
        gobject.idle_add(self.__change_theme, name, title, preview)


    def __update_list(self):
    
        w, h = self.get_size()
        themes = theme.list_themes()
        self.__themes = []
        idx = 0
        for name, preview, title, description, author in themes:
            try:
                img = gtk.gdk.pixbuf_new_from_file(preview)
            except:
                continue
                
            item = ThemeListItem(img, title, description, author)
            item.set_size(w, 80)
            item.connect_clicked(self.__on_item_clicked, preview, name, title, idx)
            
            self.__list.append_item(item)
            self.__themes.append((name, title))
            
            if (name == config.theme()):
                self.__list.set_hilight(idx)

            idx += 1
        #end for


    def __change_theme(self, t, title, preview):
                       
        #self.set_visible(False)
        
        #dlg = InfoDialog(u"Using theme \xbb%s\xab" % title, self)
        #dlg.run()
        
        config.set_theme(t)
        #config.set_thumbnails_epoch(int(time.time()))
        theme.set_theme(t)
        self.propagate_theme_change()
        
        w, h = self.get_size()
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        self.fx_slide_vertical(buf, 0, 0, w, h, self.SLIDE_DOWN)

        self.emit_message(msgs.CORE_EV_THEME_CHANGED)

