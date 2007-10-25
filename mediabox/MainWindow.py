import config

import gtk



try:
    import hildon
    IS_MAEMO = True
except:
    IS_MAEMO = False
    

class MainWindow(gtk.Window):
    """
    Class for the main window. The main window holds a stack of subwindows
    where one subwindow can be displayed at a time.
    """

    def __init__(self):
    
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)        
        if (IS_MAEMO): self.fullscreen()
        else: self.set_decorated(False)
        self.set_size_request(800, 480)

        self.__hbox = gtk.HBox()
        self.__hbox.show()
        #gtk.Window.add(self, self.__hbox)
        
        self.__fixed = gtk.Fixed()
        self.__fixed.show()
        self.add(self.__fixed)
        
        self.connect("focus-out-event", self.__on_lose_focus)
        
        
    def __on_lose_focus(self, src, ev):
    
        #print "refocus"
        self.grab_focus()
        
        
    def put(self, child, x, y):
    
        self.__fixed.put(child, x, y)
        
        
    def move(self, child, x, y):
    
        self.__fixed.move(child, x, y)
                
        

