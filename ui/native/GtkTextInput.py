from utils.EventEmitter import EventEmitter
import platforms

import gtk


class TextInput(EventEmitter):

    def __init__(self):
    
        self.__window = None
        if (platforms.MAEMO5):
            import hildon
            self.__entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        else:
            self.__entry = gtk.Entry()
    
        EventEmitter.__init__(self)


    def set_window(self, window):
    
        if (not self.__window):
            self.__window = window
            self.__init_entry()
        #end if
        
        
    def __init_entry(self):
    
        self.__window.put_widget(self.__entry, 0, 0, 10, 10)


    def set_geometry(self, x, y, w, h):
    
        self.__window.put_widget(self.__entry, x, y, w, h)


    def set_visible(self, v):
    
        if (v):
            self.__entry.show()
        else:
            self.__entry.hide()


    def set_text(self, text):

        self.__entry.set_text(text)
        

    def get_text(self):

        return self.__entry.get_text()

