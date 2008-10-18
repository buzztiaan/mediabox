from ListItem import ListItem
import theme


class FolderItem(ListItem):
    """
    List item for folders.
    """
    
    def __init__(self, f, thumbnail):
    
        ListItem.__init__(self, f, thumbnail)
        self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play))

