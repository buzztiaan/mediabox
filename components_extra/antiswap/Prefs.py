from com import Configurator, msgs
from ui.Label import Label
from ui.CheckBox import CheckBox
from ui.layout import VBox
from theme import theme


class Prefs(Configurator):

    ICON = theme.fmradio_viewer_radio
    TITLE = "RAM Allocation"

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)
                
        chk = CheckBox(True)
        chk.connect_checked(self.__on_check)
        self.__vbox.add(chk)
        lbl = Label("Continuously allocate RAM\n"
                    "(takes effect after restarting MediaBox)",
                    theme.font_mb_plain, theme.color_mb_listitem_text)        
        chk.add(lbl)

        lbl = Label("MediaBox can run smoother on the Nokia 770 when\n"
                    "continuously allocating RAM. This prevents the device\n"
                    "from swapping out parts of MediaBox.",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)




    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_check(self, value):

        pass

