from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
from theme import theme


class HeaderItem(ButtonListItem):
    """
    List item for the header.
    """

    BUTTON_PLAY = "play"
    BUTTON_ENQUEUE = "enqueue"
    BUTTON_ADD_TO_LIBRARY = "add-to-library"
    BUTTON_REMOVE = "remove"
    BUTTON_REMOVE_PRECEDING = "remove-preceding"
    BUTTON_REMOVE_SUCCEEDING = "remove-succeeding"
    BUTTON_OPEN = "open"

    def __init__(self, title):

        self.__label = self.escape_xml(title)
        self.__info = ""

        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)



    def set_info(self, text):
    
        self.__info = text
        self.invalidate()


    def render_this(self, cnv):
    
        self.render_bg(cnv)
        self.render_label(cnv, 24, self.__label, self.__info)
        self.render_buttons(cnv)

