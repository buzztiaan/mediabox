from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
import theme


class ListItem(ButtonListItem):
    """
    List item for files.
    """

    BUTTON_PLAY = "play"
    BUTTON_ENQUEUE = "enqueue"
    BUTTON_ADD_TO_LIBRARY = "add-to-library"


    _ITEMS_CLOSED = [theme.mb_item_btn_menu]
    _ITEMS_OPEN = [theme.mb_item_btn_play, theme.mb_item_btn_enqueue]

    _BUTTONS = [ButtonListItem.BUTTON_MENU,
                BUTTON_PLAY, BUTTON_ENQUEUE]


    def __init__(self, f, thumbnail):

        self.__icon = thumbnail
        self.__emblem = f.emblem
        self.__source_icon = f.source_icon
        self.__label = self.escape_xml(f.name)
        self.__sublabel = self.escape_xml(f.info)
        self.__mimetype = f.mimetype
        
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)


    def set_icon(self, icon):
    
        self.__icon = icon
        

    def set_emblem(self, emblem):
    
        self.__emblem = emblem


    def render_this(self, cnv):
    
        ButtonListItem.render_this(self, cnv)
        #print "render this", self

        w, h = self.get_size()
        w = 160


        if (self.__icon):
            icon = thumbnail.draw_decorated(cnv, 4, 4, w - 8, h - 8,
                                            self.__icon, self.__mimetype)
            
            #if (self.__emblem):
            #    cnv.fit_pixbuf(self.__emblem, w - 48, h - 48, 48, 48)
        
        self.render_label(cnv, 168, self.__label, self.__sublabel)
        self.render_selection_frame(cnv)
       
        self.render_buttons(cnv)
