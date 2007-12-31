from ui.Widget import Widget
import theme


class RootPane(Widget):

    def __init__(self, esens):
    
        Widget.__init__(self, esens)
        self.set_size(800, 480)

