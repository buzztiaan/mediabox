from mediabox.TrackItem import TrackItem
import theme

import gtk


class AlbumHeader(TrackItem):
    """
    List item for album headers.
    """

    BUTTON_PLAY = "play"
    BUTTON_ADD_ALBUM = "add-album"
    BUTTON_ADD_TRACK = "add-track"

    _ITEMS_CLOSED = [theme.item_btn_enqueue]
    _ITEMS_OPEN = []

    _BUTTONS = [BUTTON_ADD_ALBUM]
    

    def __init__(self, cover, name, num_of_items):

        TrackItem.__init__(self, cover, "audio/x-music-folder",
                           name, "%d items" % num_of_items)
        self.set_graphics(theme.button_1, theme.button_2)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)
        
