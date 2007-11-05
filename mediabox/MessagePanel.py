from Panel import Panel
import theme

import gtk


class MessagePanel(Panel):

    def __init__(self):
       
        Panel.__init__(self, False)
        
        self.__message_label = gtk.Label("")
        self.__message_label.modify_font(theme.font_plain)
        self.__message_label.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__message_label.show()
        self.box.add(self.__message_label)


    def set_message(self, msg):
    
        self.__message_label.set_text(msg)

