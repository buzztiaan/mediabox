from com import Configurator, msgs
from ui.HBox import HBox
from ui.VBox import VBox
from ui.Label import Label
from ui.CheckBox import CheckBox
from ui.Button import Button
from theme import theme
from mediabox import config as mb_config


class Prefs(Configurator):

    ICON = theme.mediascanner_prefs
    TITLE = "Media Indexing"
    

    def __init__(self):
    
        Configurator.__init__(self)

        self.__vbox = VBox()
        self.__vbox.set_geometry(0, 0, 620, 370)
        self.add(self.__vbox)

        chk = CheckBox(mb_config.scan_at_startup())
        chk.connect_checked(self.__on_check)
        self.__vbox.add(chk)
        lbl = Label("Always update index at startup",
                    theme.font_mb_plain, theme.color_mb_listitem_text)        
        chk.add(lbl)

        self.__btn_reindex = Button("Update index now")
        self.__btn_reindex.connect_clicked(self.__on_click_rebuild)
        self.__vbox.add(self.__btn_reindex)

        


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__vbox.set_geometry(0, 0, w, h)
        self.__btn_reindex.set_size(w, 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
        
    def __on_check(self, value):
    
        mb_config.set_scan_at_startup(value)


    def __on_click_rebuild(self):
    
        mediaroots = mb_config.mediaroot()
        self.emit_event(msgs.CORE_ACT_SCAN_MEDIA, True)

