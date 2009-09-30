from Box import Box


class HBox(Box):

    def __init__(self):
    
        Box.__init__(self)
        self.set_orientation(self.HORIZONTAL)

