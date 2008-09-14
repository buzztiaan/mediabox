from ListItem import ListItem
import theme


class DeletableListItem(ListItem):
    """
    List item that can be deleted.
    """

    _ITEMS_CLOSED = [theme.mb_item_btn_menu]
    _ITEMS_OPEN = [theme.mb_item_btn_play, theme.mb_item_btn_enqueue,
                   theme.mb_item_btn_remove]

    _BUTTONS = [ListItem.BUTTON_MENU,
                ListItem.BUTTON_PLAY,
                ListItem.BUTTON_ENQUEUE,
                ListItem.BUTTON_REMOVE]

