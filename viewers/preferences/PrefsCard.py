import theme

import gtk
import pango


class PrefsCard(gtk.VBox):

    def __init__(self, title):
    
        self.__title = title
    
        gtk.VBox.__init__(self)
        

    def get_title(self):
    
        return self.__title
        
