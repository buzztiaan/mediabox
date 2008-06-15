from Widget import Widget


class HBox(Widget):

    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2
    

    def __init__(self):
    
        self.__spacing = 0
        self.__alignment = self.ALIGN_CENTER
    
        Widget.__init__(self)
     
     
    def set_alignment(self, alignment):
    
        self.__alignment = alignment
        self.render()
     
     
    def set_spacing(self, spacing):
    
        self.__spacing = spacing
        self.render()
     
        
    def render_this(self):
    
        w, h = self.get_size()
        children = [ c for c in self.get_children() if c.is_visible() ]
    
        total_width = reduce(lambda a,b:a+b,
                             [ c.get_physical_size()[0] for c in children ], 0)
        total_width += (len(children) - 1) * self.__spacing
        total_width = min(w, total_width)
        
        if (self.__alignment == self.ALIGN_LEFT):
            x = 0
        elif (self.__alignment == self.ALIGN_CENTER):
            x = (w - total_width) / 2
        else:
            x = w - total_width
            
        for c in children:
            width, height = c.get_physical_size()
            c.set_pos(x, (h - height) / 2)
            #print c, x, (h - height) / 2
            x += width + self.__spacing
        #end for

