from viewers.Viewer import Viewer
from PrefsThumbnail import PrefsThumbnail
from ui.ImageButton import ImageButton
from ui.Label import Label
from mediascanner.MediaItem import MediaItem
from CardMediaRoot import CardMediaRoot
from CardThemeSelector import CardThemeSelector
import theme

import gtk
import os


class Preferences(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_prefs
    ICON_ACTIVE = theme.viewer_prefs_active
    PRIORITY = 9999


    def __init__(self, esens):
    
        self.__items = []
    
        self.__current_card = None
        self.__cards = []
    
        Viewer.__init__(self, esens)


        #
        # prefs cards
        #
        self.__add_card(CardMediaRoot(esens, "Media Collection"),
                        "Media Collection", theme.prefs_folder)
        self.__add_card(CardThemeSelector(esens, "Themes"),
                        "Themes", theme.prefs_theme)
        self.__show_card(0)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        #screen.draw_pixbuf(theme.titlebar, x, y)


    def __on_observe_cards(self, src, cmd, *args):
    
        if (cmd == src.OBS_SCAN_MEDIA):
            self.update_observer(self.OBS_SCAN_MEDIA, True)


    def __show_card(self, idx):
    
        if (self.__current_card):
            self.__current_card.set_visible(False)
            
        card = self.__cards[idx]
        card.set_visible(True)
        card.render()
        self.__current_card = card
        self.update_observer(self.OBS_TITLE, card.get_title())

        
        
    def __add_card(self, card, label, icon):
            
        tn = PrefsThumbnail(icon, label)
        item = MediaItem()
        item.thumbnail_pmap = tn
        self.__items.append(item)
        
        self.add(card)
        card.set_visible(False)
        self.__cards.append(card)
        card.add_observer(self.__on_observe_cards)
        
        
    def load(self, item):
    
        idx = self.__items.index(item)
        self.__show_card(idx)
        

    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        
        
    def hide(self):

        self.update_observer(self.OBS_SCAN_MEDIA, False)    
        Viewer.hide(self)
        
