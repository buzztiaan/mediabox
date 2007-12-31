from ui.Label import Label
from Panel import Panel
import theme

import gtk


class MessagePanel(Panel):

    def __init__(self, esens):
       
        Panel.__init__(self, esens, False)
        
        self.__message_label = Label(esens, "", theme.font_headline,
                                     theme.color_fg_panel_text)
        self.__message_label.set_pos(20, 20)
        self.add(self.__message_label)


    def set_message(self, msg):
    
        self.__message_label.set_text(msg)

