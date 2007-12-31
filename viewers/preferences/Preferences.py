from viewers.Viewer import Viewer
from viewers.Thumbnail import Thumbnail
from ui.ImageButton import ImageButton
from ui.Label import Label
from PrefsItem import PrefsItem
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
        # title pane
        #
        self.__title = Label(esens, "", theme.font_headline,
                             theme.color_fg_panel_text)
        self.__title.set_pos(0, 8)
        self.add(self.__title)

        btn_minimize = ImageButton(esens, theme.prefs_btn_minimize_1,
                                   theme.prefs_btn_minimize_2)
        btn_minimize.set_pos(520, 0)
        btn_minimize.set_size(50, 50)
        self.add(btn_minimize)
        btn_minimize.connect(btn_minimize.EVENT_BUTTON_RELEASE,
                             lambda x,y:self.update_observer(self.OBS_MINIMIZE))
        
        btn_close = ImageButton(esens, theme.prefs_btn_close_1,
                                theme.prefs_btn_close_2)
        btn_close.set_pos(570, 0)
        btn_close.set_size(50, 50)        
        self.add(btn_close)
        btn_close.connect(btn_close.EVENT_BUTTON_RELEASE,
                          lambda x,y:self.update_observer(self.OBS_QUIT))

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
        
        print x, y
        screen.draw_pixbuf(theme.titlebar, x, y)



    def __show_card(self, idx):
    
        if (self.__current_card):
            self.__current_card.set_visible(False)
            
        card = self.__cards[idx]
        card.set_visible(True)
        card.render()
        self.__current_card = card
        self.__title.set_text(" " + card.get_title())

        
        
    def __add_card(self, card, label, icon):
            
        tn = Thumbnail()
        tn.fill_color(theme.color_bg)
        tn.add_image(icon, 0, 0, 160, 120)
        #tn.add_rect(0, 98, 160, 22, 0x44, 0x44, 0xff, 0xa0)
        tn.add_rect(0, 98, 160, 22, theme.color_bg_thumbnail_label, 0xa0)
        tn.add_text(label, 2, 96, theme.font_tiny,
                    theme.color_fg_thumbnail_label)
        tn.add_image(theme.btn_load, 128, 88)        
        item = PrefsItem()
        item.set_thumbnail(tn)
        self.__items.append(item)
        
        self.add(card)
        card.set_visible(False)
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
        
