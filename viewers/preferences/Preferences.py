from viewers.Viewer import Viewer
from viewers.Thumbnail import Thumbnail
from ui.ImageButton import ImageButton
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

        self.__box = gtk.VBox()
        self.set_widget(self.__box)

        #
        # title pane
        #
        panel = gtk.Layout()
        panel.set_size_request(620, 50)
        panel.show()
        self.__box.pack_start(panel, False, False)
        
        bg = gtk.Image()
        bg.set_from_pixbuf(theme.titlebar)
        bg.show()
        panel.put(bg, 0, 0)

        hbox = gtk.HBox()
        hbox.set_size_request(620, 50)
        hbox.show()
        panel.put(hbox, 0, 0)

        self.__title = gtk.Label("")
        self.__title.modify_font(theme.font_headline)
        self.__title.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__title.set_alignment(0.0, 0.5)
        self.__title.show()
        hbox.pack_start(self.__title, True, True)

        btn_minimize = ImageButton(theme.prefs_btn_minimize_1,
                                   theme.prefs_btn_minimize_2,
                                   theme.titlebar.subpixbuf(540, 0, 40, 50))
        btn_minimize.connect("button-release-event",
                             lambda x,y:self.update_observer(self.OBS_MINIMIZE))
        btn_minimize.show()
        hbox.pack_start(btn_minimize, False, False)        
        
        btn_close = ImageButton(theme.prefs_btn_close_1,
                                theme.prefs_btn_close_2,
                                theme.titlebar.subpixbuf(580, 0, 40, 50))
        btn_close.connect("button-release-event",
                          lambda x,y:self.update_observer(self.OBS_QUIT))
        btn_close.show()
        hbox.pack_start(btn_close, False, False)
                



        #
        # prefs cards
        #
        self.__add_card(CardMediaRoot("Media Collection"), "Media Collection",
                        theme.prefs_folder)
        self.__add_card(CardThemeSelector("Themes"), "Themes", theme.prefs_theme)
        self.__show_card(0)


    def __show_card(self, idx):
    
        if (self.__current_card):
            self.__current_card.hide()
            
        card = self.__cards[idx]
        card.show()
        self.__current_card = card
        self.__title.set_text(" " + card.get_title())

        
        
    def __add_card(self, card, label, icon):
            
        tn = Thumbnail()
        tn.fill(0xff, 0xff, 0xff)
        tn.add_image(icon, 0, 0, 160, 120)
        tn.add_rect(0, 98, 160, 22, 0x44, 0x44, 0xff, 0xa0)
        tn.add_text(label, 2, 96, theme.font_tiny, "#ffffff")
        tn.add_image(theme.btn_load, 128, 88)        
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
        
