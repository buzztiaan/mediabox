from mediabox.TrackItem import TrackItem
import theme


class ListItem(TrackItem):
    """
    List item for music tracks.
    """

    BUTTON_PLAY = "play"
    BUTTON_ADD_ALBUM = "add-album"
    BUTTON_ADD_TRACK = "add-track"

    _ITEMS_CLOSED = [theme.mb_item_btn_menu]
    _ITEMS_OPEN = [theme.mb_item_btn_play, theme.mb_item_btn_enqueue]

    _BUTTONS = [TrackItem.BUTTON_MENU,
                BUTTON_PLAY, BUTTON_ADD_TRACK]


    def __init__(self, label, sublabel):

        TrackItem.__init__(self, None, "", label, sublabel)

