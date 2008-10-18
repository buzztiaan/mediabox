from mediabox.TrackItem import TrackItem
import theme


class ListItem(TrackItem):
    """
    List item for music tracks.
    """

    BUTTON_PLAY = "play"
    BUTTON_ADD_ALBUM = "add-album"
    BUTTON_ADD_TRACK = "add-track"



    def __init__(self, label, sublabel):

        TrackItem.__init__(self, None, "", label, sublabel)
        self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play),
                         (self.BUTTON_ADD_TRACK, theme.mb_item_btn_enqueue))
