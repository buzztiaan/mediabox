from ui.ButtonListItem import ButtonListItem
import theme


class ThemeListItem(ButtonListItem):
    """
    List item for themes.
    """

    BUTTON_PLAY = "play"


    def __init__(self, preview, name, info):

        self.__preview = preview
        self.__label = self.escape_xml(name)
        self.__info = self.escape_xml(info)
        
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)

        self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play))


    def render_this(self, cnv):
    
        self.render_bg(cnv)

        w, h = self.get_size()
        icon_y = (h - self.__preview.get_height()) / 2
        cnv.draw_pixbuf(self.__preview, 8, icon_y)

        self.render_label(cnv, 128, self.__label, self.__info)
        self.render_selection_frame(cnv)
             
        if (not self.is_hilighted()):
            self.render_buttons(cnv)

