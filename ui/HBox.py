from Widget import Widget


class HBox(Widget):

    def __init__(self, esens):
    
        Widget.__init__(self, esens)
        
        
    def get_pos(self):
    
        return (0, 0)
        
        
    def get_size(self):
    
        return self.get_parent().get_size()
        
        
    def render_this(self):
    
        w, h = self.get_size()
        children = self.get_children()
    
        total_width = reduce(lambda a,b:a+b,
                             [ c.get_physical_size()[0] for c in children ])
        total_width = min(w, total_width)
        
        x = (w - total_width) / 2
        for c in children:
            width, height = c.get_physical_size()
            c.set_pos(x, (h - height) / 2)
            x += width
        #end for

