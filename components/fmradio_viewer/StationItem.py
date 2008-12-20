from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
from theme import theme


class StationItem(ButtonListItem):
    """
    List item for radio stations.
    """

    BUTTON_PLAY = "play"
    BUTTON_RENAME = "rename"
    BUTTON_REMOVE = "remove"


    def __init__(self, freq, name):

        self.__title = self.escape_xml(name)
        self.__freq = freq      
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)
        self.set_grip(theme.mb_item_grip)
        self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play),
                         (self.BUTTON_REMOVE, theme.mb_item_btn_remove))
        

    def render_this(self, cnv):
    
        self.render_bg(cnv)
        self.render_grip(cnv)
        self.render_label(cnv, 32, self.__title, self.__freq)
        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

