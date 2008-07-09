from ui.Widget import Widget


class MediaWidget(Widget):

    def __init__(self):
    
        Widget.__init__(self)
        
        
    def load(self, uri):
    
        raise NotImplementedError
