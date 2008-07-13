from StripItem import StripItem
import theme


class ListItem(StripItem):
    """
    Base class for regular hilightable list items.
    """

    def __init__(self):

        self.__normal_bg = None
        self.__hilighted_bg = None

        self.__color_1 = "#000000"
        self.__color_2 = "#666666"
        self.__font = None
        self.__grip = None
        
        StripItem.__init__(self)


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
       
        
    def render_this(self, cnv):

        w, h = self.get_size()    
        cnv.fill_area(0, 0, w, h, theme.color_bg)        

        background = self.is_hilighted() and self.__hilighted_bg \
                                         or self.__normal_bg

        if (background):
            cnv.draw_frame(background, 0, 0, w, h, True)

        x = 0
        if (self.__grip):
            x += 4
            cnv.draw_pixbuf(self.__grip, x, 0)
            x += 24
