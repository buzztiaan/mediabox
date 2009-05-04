"""
Layouter for holding one child widget.
"""

from Widget import Widget


class BoxLayout(Widget):
    """
    Layouter for holding exactly one child widget. The child is stretched across
    the box.
    
    @deprecated: use a L{HBox} or L{VBox} with a single dynamically sized
                 child instead
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

