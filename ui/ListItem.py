"""
Base class for list items.
"""

from StripItem import StripItem
import theme


class ListItem(StripItem):
    """
    Base class for regular hilightable list items.
    """

    def __init__(self):

        self.__normal_bg = theme.mb_listitem_bg
        self.__hilighted_bg = theme.mb_listitem_bg

        self.__color_1 = theme.color_fg_item
        self.__color_2 = theme.color_fg_item_2
        self.__font = theme.font_plain
        self.__grip = None
        
        StripItem.__init__(self)
        self.set_selection_frame(theme.mb_selection_frame)


    @staticmethod
    def escape_xml(s):
        
        s = s.decode("utf-8", "replace").encode("utf-8")
        return s.replace("<", "&lt;") \
                .replace(">", "&gt;") \
                .replace("&", "&amp;")
        

    def set_graphics(self, normal, hilighted):
    
        self.__normal_bg = normal
        self.__hilighted_bg = hilighted


    def set_grip(self, pbuf):
    
        self.__grip = pbuf
     

    def set_colors(self, col1, col2):
    
        self.__color_1 = col1
        self.__color_2 = col2
        
        
    def set_font(self, font):
    
        self.__font = font  

       
    def render_label(self, canvas, x, label1, label2 = ""):
    
        canvas.draw_text("%s\n<span color='%s'>%s</span>" \
                          % (label1, self.__color_2, label2),
                             self.__font, x, 8,
                             self.__color_1, use_markup = True)        
    
    
    def render_grip(self, cnv):
    
        if (self.__grip):
            w, h = self.get_size()
            cnv.draw_pixbuf(self.__grip, 4, (h - self.__grip.get_height()) / 2)
            
        
    def render_this(self, cnv):

        w, h = self.get_size()
        cnv.fill_area(0, 0, w, h, theme.color_bg)        

        background = self.is_hilighted() and self.__hilighted_bg \
                                         or self.__normal_bg

        if (background):
            cnv.draw_frame(background, 0, 0, w, h, True)

