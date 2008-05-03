from mediabox.TrackItem import TrackItem
import theme

import gtk


class AlbumHeader(TrackItem):
    """
    List item for album headers.
    """

    _ITEMS_CLOSED = [theme.item_btn_enqueue]
    _ITEMS_OPEN = []

    _BUTTONS = ["add"]
    

    def __init__(self, cover, name, num_of_items):

        try:
            cover = gtk.gdk.pixbuf_new_from_file(cover)
        except:
            cover = theme.viewer_music_unknown

        cover = cover.scale_simple(64, 64, gtk.gdk.INTERP_BILINEAR)


        TrackItem.__init__(self, cover, name, "%d items" % num_of_items)
        self.set_graphics(theme.button_1, theme.button_2)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)
        