from ui.ButtonListItem import ButtonListItem
import theme


class ThemeListItem(ButtonListItem):
    """
    List item for themes.
    """

    BUTTON_PLAY = "play"

    _ITEMS_CLOSED = [theme.mb_item_btn_play]
    _ITEMS_OPEN = []

    _BUTTONS = [BUTTON_PLAY]


    def __init__(self, preview, name, info):

        self.__preview = preview
        self.__label = self.escape_xml(name)
        self.__info = self.escape_xml(info)
        
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)



    def render_this(self, cnv):
    
        ButtonListItem.render_this(self, cnv)
        #print "render this", self

        w, h = self.get_size()
        icon_y = (h - self.__preview.get_height()) / 2
        cnv.draw_pixbuf(self.__preview, 8, icon_y)

        self.render_label(cnv, 128, self.__label, self.__info)
        self.render_selection_frame(cnv)
             
        if (not self.is_hilighted()):
            self.render_buttons(cnv)

