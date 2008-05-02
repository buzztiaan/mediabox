from mediabox.TrackItem import TrackItem
import theme


class ListItem(TrackItem):
    """
    List item for music tracks.
    """

    _ITEMS_CLOSED = [theme.item_btn_menu]
    _ITEMS_OPEN = [theme.item_btn_play, theme.item_btn_enqueue]

    _BUTTONS = ["menu", "play", "add"]


    def __init__(self, label, sublabel):

        TrackItem.__init__(self, None, label, sublabel)
        self.set_graphics(theme.item, theme.item_active)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)

