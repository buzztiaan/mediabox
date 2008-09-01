from ListItem import ListItem
import theme


class FolderItem(ListItem):
    """
    List item for folders.
    """

    _ITEMS_CLOSED = [theme.mb_item_btn_play]
    _ITEMS_OPEN = []

    _BUTTONS = [ListItem.BUTTON_PLAY]

