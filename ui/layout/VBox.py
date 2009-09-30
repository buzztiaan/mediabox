from Box import Box


class VBox(Box):

    def __init__(self):
    
        Box.__init__(self)
        self.set_orientation(self.VERTICAL)

