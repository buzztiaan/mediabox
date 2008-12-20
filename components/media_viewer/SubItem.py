from ListItem import ListItem
from theme import theme


class SubItem(ListItem):

    def __init__(self, f):

        self.__label = self.escape_xml(f.name)
        self.__sublabel = self.escape_xml(f.info)
            
        ListItem.__init__(self, f, None)
        self.set_background(theme.mb_subitem_bg)
        
        
        
    def render_this(self, cnv):
    
        self.render_bg(cnv)
        w, h = self.get_size()
        #cnv.fill_area(0, 0, w, h, "#dddddd")
        self.render_label(cnv, 48, self.__label, self.__sublabel)
        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

