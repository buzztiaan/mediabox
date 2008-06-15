from mediabox.TrackItem import TrackItem
import theme

import gtk


class PlaylistItem(TrackItem):
    """
    List item for play list entries.
    """

    BUTTON_PLAY = "play"
    BUTTON_REMOVE = "remove"
    BUTTON_REMOVE_FOLLOWING = "remove-following"
    BUTTON_REMOVE_PRECEEDING = "remove-preceeding"

    _ITEMS_CLOSED = [theme.item_btn_menu]
    _ITEMS_OPEN = [theme.item_btn_play, theme.item_btn_remove,
                   theme.item_btn_remove_down, theme.item_btn_remove_up]
        
    _BUTTONS = [TrackItem.BUTTON_MENU,
                BUTTON_PLAY, BUTTON_REMOVE,
                BUTTON_REMOVE_FOLLOWING,
                BUTTON_REMOVE_PRECEEDING]


    def __init__(self, cover, label, sublabel):

        try:
            cover = gtk.gdk.pixbuf_new_from_file(cover)
        except:
            cover = theme.viewer_music_unknown

        cover = cover.scale_simple(64, 64, gtk.gdk.INTERP_BILINEAR)
    
        TrackItem.__init__(self, cover, label, sublabel)
        self.set_graphics(theme.item, theme.item_active)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)
        self.set_grip(theme.item_grip)
