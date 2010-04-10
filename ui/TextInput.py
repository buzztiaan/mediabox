from Widget import Widget
import platforms
from Pixmap import text_extents
from theme import theme

try:
    import gtk
except:
    gtk = None

try:
    import hildon
except:
    hildon = None


class TextInput(Widget):

    def __init__(self):
    
        Widget.__init__(self)

        if (platforms.MAEMO5):
            self.__input = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        else:
            self.__input = gtk.Entry()
        
        
    def _visibility_changed(self):
    
        if (self.is_visible()):
            self.__input.show()
        else:
            self.__input.hide()


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()        
        window = self.get_window()

        window.put_widget(self.__input, x, y, w, -1)


    def set_text(self, text):

        self.__input.set_text(text)
        

    def get_text(self):

        return self.__input.get_text()

