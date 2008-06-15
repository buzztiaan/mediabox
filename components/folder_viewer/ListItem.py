from mediabox.TrackItem import TrackItem
import theme


class ListItem(TrackItem):
    """
    List item for files.
    """

    BUTTON_PLAY = "play"


    _ITEMS_CLOSED = [theme.item_btn_play]
    _ITEMS_OPEN = []

    _BUTTONS = [BUTTON_PLAY]


    def __init__(self, icon, label, sublabel):

        TrackItem.__init__(self, icon, label, sublabel)
        self.set_graphics(theme.item, theme.item_active)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)

