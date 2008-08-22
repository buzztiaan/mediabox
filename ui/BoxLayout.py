from Widget import Widget


class BoxLayout(Widget):
    """
    Layout for holding exactly one child widget. The child is stretched across
    the box.
    """

    def __init__(self):
    
        Widget.__init__(self)
        
        
    def render_this(self):
    
        try:
            child = self.get_children()[0]
        except:
            return
            
        w, h = self.get_size()
        child.set_geometry(0, 0, w, h)

