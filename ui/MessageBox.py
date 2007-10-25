from TranslucentWindow import TranslucentWindow
from mediabox import config

import gtk
import pango



class MessageBox(TranslucentWindow):
    """
    Class for a (modal) message box.
    """
    
    
    TYPE_INFO = 0
    TYPE_WARNING = 1
    TYPE_ERROR =  2
    TYPE_QUESTION = 3
    
    
    __ICON_MAP = {TYPE_INFO: "gfx/dialog-info.png",
                  TYPE_WARNING: "gfx/dialog-warning.png",
                  TYPE_ERROR: "gfx/dialog-error.png",
                  TYPE_QUESTION: "gfx/dialog-question.png"}
    

    def __init__(self):
    
        self.__return_value = -1
        self.__running = False
        
        self.__buttons = []
        
    
        TranslucentWindow.__init__(self)
        self.set_size_request(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)                 

        img = gtk.Image()
        img.set_from_file("gfx/panel.png")
        img.show()               
        #self.put(img, 200, 200)
        
        self.__icon = gtk.Image()
        self.__icon.show()
        self.put(self.__icon, 140, 120)
        
        self.__label1 = gtk.Label("")
        self.__label1.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.__label1.modify_font(pango.FontDescription("Sans bold 20"))
        self.__label1.show()
        self.put(self.__label1, 300, 100)

        self.__label2 = gtk.Label("")
        self.__label2.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#b0b0b0"))
        self.__label2.modify_font(pango.FontDescription("Sans 18"))
        self.__label2.show()
        self.put(self.__label2, 300, 160)


        
        self.connect("button-press-event", self.__on_click)
        
        
    def __on_click(self, src, ev):
    
        px, py = src.get_pointer()
        
        if (300 <= py <= 380):
            x = config.SCREEN_WIDTH / 2 - (len(self.__buttons) * 120) / 2
            idx = (px - x) / 120
            
            if (0 <= idx < len(self.__buttons)):
                self.__return_value = idx        
                self.__running = False
        #end if



    def __make_buttons(self, buttons):
    
        while (self.__buttons):
            self.__buttons.pop().destroy()
            
        x = config.SCREEN_WIDTH / 2 - (len(buttons) * 120) / 2
        for name in buttons:
            btn = gtk.Label(name)
            #btn.set_size_request(120, 80)
            btn.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
            btn.modify_font(pango.FontDescription("Sans bold 20"))
            btn.show()
            self.put(btn, x, 300)
            self.__buttons.append(btn)
            x += 120


    def run(self, mtype, message1, message2, buttons = []):
    
        self.__icon.set_from_file(self.__ICON_MAP[mtype])
        self.__label1.set_text(message1)
        self.__label2.set_text(message2)
        self.__label2.get_layout().set_width(pango.SCALE * 300)

        self.__make_buttons(buttons)
        self.show()


    def run_modal(self, *args):
        
        self.__running = True
        self.run(*args)
        
        while (self.__running):
            gtk.main_iteration()
        
        return self.__return_value
        
