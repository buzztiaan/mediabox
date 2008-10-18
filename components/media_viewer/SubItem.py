from ListItem import ListItem


class SubItem(ListItem):

    def __init__(self, f):

        self.__label = self.escape_xml(f.name)
        self.__sublabel = self.escape_xml(f.info)
            
        ListItem.__init__(self, f, None)
        
        
        
    def render_this(self, cnv):
    
        self.render_bg(cnv)       
        self.render_label(cnv, 48, self.__label, self.__sublabel)
        self.render_selection_frame(cnv)
        self.render_buttons(cnv)

