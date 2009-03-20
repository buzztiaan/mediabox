from ListItem import ListItem
from mediabox import thumbnail


class MediaItem(ListItem):

    def __init__(self, f, icon):

        self.__label = self.escape_xml(f.name)
        self.__letter = self.__label and unicode(self.__label)[0].upper() or " "
        self.__sublabel = self.escape_xml(f.info)

        ListItem.__init__(self, f, icon)


    def get_letter(self):
    
        return self.__letter


    def set_info(self, info):
    
        self.__sublabel = info
        self.invalidate()        


    def render_this(self, cnv):
    
        self.render_bg(cnv)
    
        w, h = self.get_size()

        self.render_icon(cnv, 8, 8, 120, h - 16)
        self.render_label(cnv, 130 + 8, self.__label, self.__sublabel)
        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

