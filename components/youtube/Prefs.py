from com import Configurator, msgs
from ui.Label import Label
import theme


class Prefs(Configurator):

    ICON = theme.youtube_device
    TITLE = "YouTube"

    def __init__(self):
    
        Configurator.__init__(self)
        
        lbl = Label("to be done...", theme.font_plain, theme.color_fg_item)
        lbl.set_pos(10, 10)
        lbl.set_visible(True)
        self.add(lbl)

