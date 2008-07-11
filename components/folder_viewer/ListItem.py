from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
import theme


class ListItem(ButtonListItem):
    """
    List item for files.
    """

    BUTTON_PLAY = "play"


    _ITEMS_CLOSED = [theme.item_btn_play]
    _ITEMS_OPEN = []

    _BUTTONS = [BUTTON_PLAY]


    def __init__(self, f, thumbnail):

        self.__thin_mode = False
        self.__icon = thumbnail
        self.__emblem = f.emblem
        self.__label = f.name
        self.__sublabel = f.info
        self.__mimetype = f.mimetype
        
        
        ButtonListItem.__init__(self)
        
        self.set_graphics(theme.item, theme.item_active)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)


    def set_icon(self, icon):
    
        self.__icon = icon
        

    def set_emblem(self, emblem):
    
        self.__emblem = emblem


    def set_thin_mode(self, value):
    
        self.__thin_mode = value
        self.invalidate()


    def render_this(self, cnv):
    
        ButtonListItem.render_this(self, cnv)

        if (self.__icon):
            icon = thumbnail.draw_decorated(cnv, 4, 4, 120, 90, #120, 70,
                                            self.__icon, self.__mimetype)
            
            if (self.__emblem):
                cnv.fit_pixbuf(self.__emblem, 70, 32, 48, 48)
        
        if (self.__thin_mode):
            cnv.draw_pixbuf(theme.caption_bg, 0, 68)
            cnv.draw_text(self.__label, theme.font_tiny, 2, 66,
                           theme.color_fg_thumbnail_label)
            cnv.draw_pixbuf(theme.btn_load, 98, 58)
        else:
            self.render_label(cnv, 128, self.__label, self.__sublabel)
            
        self.render_buttons(cnv)
