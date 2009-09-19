from HBox import _Box


class VBox(_Box):

    def __init__(self):
    
        _Box.__init__(self)
        self.set_mode(self.VERTICAL)

