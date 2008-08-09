from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
import theme


class HeaderItem(ButtonListItem):
    """
    List item for the header.
    """

    BUTTON_PLAY = "play"
    BUTTON_ENQUEUE = "enqueue"


    _ITEMS_CLOSED = [theme.item_btn_enqueue]
    _ITEMS_OPEN = []

    _BUTTONS = [BUTTON_ENQUEUE]


    def __init__(self, title):

        self.__label = self.escape_xml(title)
        self.__info = ""

        ButtonListItem.__init__(self)
        self.set_graphics(theme.button_1, theme.button_2)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)


    def set_info(self, text):
    
        self.__info = text
        self.invalidate()


    def render_this(self, cnv):
    
        ButtonListItem.render_this(self, cnv)
        self.render_label(cnv, 24, self.__label, self.__info)
        self.render_buttons(cnv)

