from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
from theme import theme


class ListItem(ButtonListItem):
    """
    List item for files.
    """

    BUTTON_PLAY = "play"
    BUTTON_ENQUEUE = "enqueue"
    BUTTON_ADD_TO_LIBRARY = "add-to-library"
    BUTTON_REMOVE = "remove"
    BUTTON_OPEN = "open"
    BUTTON_CLOSE = "close"


    def __init__(self, f, thumbnail):

        self.__icon = thumbnail or ""
        self.__file = f
        
        
        ButtonListItem.__init__(self)        
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)
        
        
    def get_file(self):
    
        return self.__file


    def set_icon(self, icon):
    
        self.__icon = icon or ""


    def render_icon(self, cnv, x, y, w, h):

        #if (self.__icon):
        thumbnail.render_on_canvas(cnv, x, y, w, h,
                                    self.__icon, self.__file.mimetype)

