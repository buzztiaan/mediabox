from ListItem import ListItem
from mediabox import thumbnail


class MediaItem(ListItem):

    def __init__(self, f, icon):

        self.__grip_visible = False
        
        self.__file = f
        self.__label = self.escape_xml(f.name)
        self.__letter = self.__label and unicode(self.__label)[0].upper() or " "
        self.__sublabel = self.escape_xml(f.info)

        ListItem.__init__(self, f, icon)


    def get_file(self):
    
        return self.__file


    def get_letter(self):
    
        return self.__letter


    def set_info(self, info):
    
        self.__sublabel = info
        self.invalidate()
        
         
    def set_grip_visible(self, v):
        
        self.__grip_visible = v


    def render_this(self, cnv):
    
        self.render_bg(cnv)
    
        w, h = self.get_size()

        x = 0
        if (self.__grip_visible):
            self.render_grip(cnv)
            x += 48
        else:
            x += 16
        self.render_icon(cnv, x, 8, 120, h - 16)
        x += 144
        self.render_label(cnv, x, self.__label, self.__sublabel)
        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

