from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
import theme

import gtk


class PlaylistItem(ButtonListItem):
    """
    List item for play list entries.
    """

    BUTTON_PLAY = "play"
    BUTTON_REMOVE = "remove"
    BUTTON_REMOVE_FOLLOWING = "remove-following"
    BUTTON_REMOVE_PRECEEDING = "remove-preceeding"

    _ITEMS_CLOSED = [theme.mb_item_btn_menu]
    _ITEMS_OPEN = [theme.mb_item_btn_play, theme.mb_item_btn_remove,
                   theme.mb_item_btn_remove_down, theme.mb_item_btn_remove_up]
        
    _BUTTONS = [ButtonListItem.BUTTON_MENU,
                BUTTON_PLAY, BUTTON_REMOVE,
                BUTTON_REMOVE_FOLLOWING,
                BUTTON_REMOVE_PRECEEDING]


    def __init__(self, thumb, f):

        self.__icon_path = thumb
        self.__source_icon = f.source_icon
        self.__mimetype = f.mimetype
        self.__label = self.escape_xml(f.name)
        self.__sublabel = self.escape_xml(f.info)

        ButtonListItem.__init__(self)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)        
        self.set_grip(theme.mb_item_grip)
        
       
        
    def render_this(self, cnv):
    
        ButtonListItem.render_this(self, cnv)

        w, h = self.get_size()
        w = 160
        x = 0
        
        self.render_grip(cnv)
        x += 24

        if (self.__icon_path):
            x += 4
            icon = thumbnail.draw_decorated(cnv, x, 4, w - 8, h - 8,
                                            self.__icon_path, self.__mimetype)
            x += w - 8
        
        x += 8
        if (self.__source_icon):
            cnv.fit_pixbuf(self.__source_icon, x, 4, 32, 32)
        self.render_label(cnv, x , "\t" + self.__label, self.__sublabel)

        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

