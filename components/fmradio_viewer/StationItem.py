from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
import theme


class StationItem(ButtonListItem):
    """
    List item for radio stations.
    """

    BUTTON_PLAY = "play"
    BUTTON_RENAME = "rename"
    BUTTON_REMOVE = "remove"


    _ITEMS_CLOSED = [theme.mb_item_btn_menu]
    _ITEMS_OPEN = [theme.mb_item_btn_play,
                   theme.mb_item_btn_remove]

    _BUTTONS = [ButtonListItem.BUTTON_MENU,
                BUTTON_PLAY, BUTTON_REMOVE]


    def __init__(self, freq, name):

        self.__title = self.escape_xml(name)
        self.__freq = freq      
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)
        self.set_grip(theme.mb_item_grip)
        

    def render_this(self, cnv):
    
        self.render_bg(cnv)
        self.render_grip(cnv)
        self.render_label(cnv, 32, self.__title, self.__freq)
        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

