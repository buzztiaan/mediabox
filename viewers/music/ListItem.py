from ui.Item import Item
import theme


class ListItem(Item):
    """
    List item for music tracks.
    """

    def __init__(self, width, height, label, sublabel):
    
        label = label.decode("utf-8", "replace").encode("utf-8")
        sublabel = sublabel.decode("utf-8", "replace").encode("utf-8")
        self.__label = label.replace("<", "&lt;") \
                            .replace(">", "&gt;") \
                            .replace("&", "&amp;")
        self.__sublabel = sublabel.replace("<", "&lt;") \
                                  .replace(">", "&gt;") \
                                  .replace("&", "&amp;")
           
        Item.__init__(self,width, height)
        self.set_graphics(theme.item, theme.item_active)
        
        
    def _render(self, canvas):
    
        Item._render(self, canvas)
        canvas.draw_text("%s\n<span color='%s'>%s</span>" \
                      % (self.__label, theme.color_fg_item_2, self.__sublabel),
                         theme.font_plain, 8, 8,
                         theme.color_fg_item, use_markup = True)

        if (not self.is_hilighted()):
            canvas.draw_pixbuf(theme.btn_load, 540, 24)

