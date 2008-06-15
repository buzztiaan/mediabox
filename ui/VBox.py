from Widget import Widget


class VBox(Widget):

    def __init__(self):
    
        Widget.__init__(self)


    def render_this(self):
    
        w, h = self.get_size()
        children = [ c for c in self.get_children() if c.is_visible() ]
    
        total_height = reduce(lambda a,b:a+b,
                             [ c.get_physical_size()[1] for c in children ], 0)
        total_height = min(h, total_height)
        
        y = (h - total_height) / 2
        for c in children:
            width, height = c.get_physical_size()
            c.set_pos((w - width) / 2, y)
            y += height
        #end for

