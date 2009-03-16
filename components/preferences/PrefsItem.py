from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
from theme import theme


class PrefsItem(ButtonListItem):
    """
    List item for play list entries.
    """

    BUTTON_PLAY = "play"


    def __init__(self, configurator):

        self.__configurator = configurator

        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)        

        self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play))
        
        
    def get_configurator(self):
    
        return self.__configurator
        
        
    def render_this(self, cnv):
    
        self.render_bg(cnv)

        w, h = self.get_size()
        w = 160
        
        x = 32
        icon_path = self.__configurator.ICON.get_path()
        icon = thumbnail.render_on_canvas(cnv, x, 4, 120, h - 8,
                                          icon_path, "application/x-other")
        x += 162
        
        name = self.__configurator.TITLE
        description = self.__configurator.DESCRIPTION
        self.render_label(cnv, x , name, description)

        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

