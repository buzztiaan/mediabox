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


    def __init__(self, f, thumbnail):

        self.__icon = thumbnail
        self.__emblem = f.emblem
        self.__source_icon = f.source_icon
        self.__mimetype = f.mimetype
        
        
        ButtonListItem.__init__(self)        
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)
        


    def set_icon(self, icon):
    
        self.__icon = icon
        

    def set_emblem(self, emblem):
    
        self.__emblem = emblem


    def render_icon(self, cnv, x, y, w, h):

        if (self.__icon):
            icon = thumbnail.render_on_canvas(cnv, x, y, w - 8, h - 8,
                                              self.__icon, self.__mimetype)

