from viewers.Viewer import Viewer
from viewers.Thumbnail import Thumbnail
from PrefsItem import PrefsItem
from CardMediaRoot import CardMediaRoot
from CardThemeSelector import CardThemeSelector
import theme

import gtk
import os


class Preferences(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_prefs
    PRIORITY = 9999
    BORDER_WIDTH = 0
    IS_EXPERIMENTAL = False


    def __init__(self):
    
        self.__items = []
    
        self.__current_card = None
        self.__cards = []
    
        Viewer.__init__(self)
                
        self.__box = gtk.HBox()
        self.set_widget(self.__box)                
                        
        self.__add_card(CardMediaRoot("Location of Media"), "Media", theme.prefs_folder)
        self.__add_card(CardThemeSelector("Current Theme"), "Themes", theme.prefs_theme)
        self.__show_card(0)


    def __show_card(self, idx):
    
        if (self.__current_card):
            self.__current_card.hide()
            
        card = self.__cards[idx]
        card.show()
        self.__current_card = card

        
        
    def __add_card(self, card, label, icon):
            
        tn = Thumbnail()
        tn.fill(0xff, 0xff, 0xff)
        tn.add_image(icon, 0, 0, 160, 120)
        tn.add_rect(0, 98, 160, 22, 0x44, 0x44, 0xff, 0xa0)
        tn.add_text(label, 2, 96, theme.font_tiny, "#ffffff")
        item = PrefsItem()
        item.set_thumbnail(tn)
        self.__items.append(item)
            
        self.__box.add(card)
        self.__cards.append(card)
        
        
    def load(self, item):
    
        idx = self.__items.index(item)
        self.__show_card(idx)
        

    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        
        
    def hide(self):
    
        Viewer.hide(self)
        self.update_observer(self.OBS_SCAN_MEDIA)
        
