from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
from theme import theme

import gtk


class PlaylistItem(ButtonListItem):
    """
    List item for play list entries.
    """

    BUTTON_PLAY = "play"
    BUTTON_REMOVE = "remove"
    BUTTON_REMOVE_FOLLOWING = "remove-following"
    BUTTON_REMOVE_PRECEEDING = "remove-preceeding"


    def __init__(self, thumb, f):

        self.__icon_path = thumb
        if (f):
            self.__source_icon = f.source_icon
            self.__mimetype = f.mimetype
            self.__label = self.escape_xml(f.name)
            self.__sublabel = self.escape_xml(f.info)
        else:
            self.__source_icon = ""
            self.__mimetype = "application/x-unknown"
            self.__label = "Currently unavailable"
            self.__sublabel = ""

        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)        
        self.set_grip(theme.mb_item_grip)
        
        if (f):
            self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play),
                             (self.BUTTON_REMOVE, theme.mb_item_btn_remove),
                             (self.BUTTON_REMOVE_FOLLOWING, theme.mb_item_btn_remove_down),
                             (self.BUTTON_REMOVE_PRECEEDING, theme.mb_item_btn_remove_up))       
        
        
    def render_this(self, cnv):
    
        self.render_bg(cnv)

        w, h = self.get_size()
        w = 160
        x = 0
        
        self.render_grip(cnv)
        x += 24

        if (self.__icon_path):
            x += 4
            icon = thumbnail.render_on_canvas(cnv, x, 4, w - 8, h - 8,
                                              self.__icon_path, self.__mimetype)
            x += w - 8
        
        x += 8
        if (self.__source_icon):
            cnv.fit_pixbuf(self.__source_icon, x, 4, 32, 32)
        self.render_label(cnv, x , "\t" + self.__label, self.__sublabel)

        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

