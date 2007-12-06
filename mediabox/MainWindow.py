import config

import gtk



try:
    import hildon
    IS_MAEMO = True

except:
    IS_MAEMO = False



_Window = IS_MAEMO and hildon.Window or gtk.Window



class MainWindow(_Window):

    def __init__(self):
    
        if (IS_MAEMO):
            _Window.__init__(self)
            self.fullscreen()
        else:
            _Window.__init__(self, gtk.WINDOW_TOPLEVEL)
            self.set_decorated(False)

        self.set_size_request(800, 480)

        self._hbox = gtk.HBox()
        self._hbox.show()
        
        self._fixed = gtk.Fixed()
        self._fixed.show()
        self.add(self._fixed)      


    def put(self, child, x, y):
    
        self._fixed.put(child, x, y)
        
        
    def move(self, child, x, y):
    
        self._fixed.move(child, x, y)

