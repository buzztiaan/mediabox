from Panel import Panel
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
import panel_actions
import theme
import caps

import gtk
import pango


class ControlPanel(Panel):   

    def __init__(self):
    
        Panel.__init__(self)                

        self.__btn_play = self._create_button(theme.btn_play_1,        
                                              theme.btn_play_2,
                     lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))

        self.__btn_pause = self._create_button(theme.btn_pause_1,        
                                               theme.btn_pause_2,
                     lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))
        
        self.__btn_record = self._create_button(theme.btn_record_1,        
                                                theme.btn_record_2,
                     lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))        

        self.__progress = ProgressBar()
        self.__progress.connect("button-release-event", self.__on_set_position)
        self.__progress.show()
        self.box.pack_start(self.__progress, False, False)
        
        self.__tuner = ProgressBar()
        self.__tuner.connect("button-release-event", self.__on_tune)
        self.__tuner.show()
        self.box.pack_start(self.__tuner, False, False)

        self.__btn_previous = self._create_button(theme.btn_previous_1,        
                                                  theme.btn_previous_2,
                     lambda x,y:self.update_observer(panel_actions.PREVIOUS))
        self.__btn_next = self._create_button(theme.btn_next_1,        
                                              theme.btn_next_2,
                     lambda x,y:self.update_observer(panel_actions.NEXT))

        self.__btn_add = self._create_button(theme.btn_add_1,        
                                              theme.btn_add_2,
                     lambda x,y:self.update_observer(panel_actions.ADD))



    def __on_set_position(self, src, ev):
    
        w, h = src.window.get_size()
        x, y = src.get_pointer()
        pos = max(0, min(99.9, x / float(w) * 100))
        self.update_observer(panel_actions.SET_POSITION, pos)
        
        
    def __on_tune(self, src, ev):

        w, h = src.window.get_size()
        x, y = src.get_pointer()
        pos = max(0, min(99.9, x / float(w) * 100))
        self.update_observer(panel_actions.TUNE, pos)    
    
                
        
    def set_capabilities(self, capabilities):
    
        if (capabilities & caps.PLAYING):
            self.__btn_play.show()
            self.__btn_pause.hide()
        else:
            self.__btn_play.hide()
            self.__btn_pause.hide()
            
        if (capabilities & caps.SKIPPING):
            self.__btn_previous.show()
            self.__btn_next.show()
        else:
            self.__btn_previous.hide()
            self.__btn_next.hide()

        if (capabilities & caps.POSITIONING):
            self.__progress.show()
        else:
            self.__progress.hide()
            
        if (capabilities & caps.TUNING):
            self.__tuner.show()
        else:
            self.__tuner.hide()
            
        if (capabilities & caps.RECORDING):
            self.__btn_record.show()
        else:
            self.__btn_record.hide()
            
        if (capabilities & caps.ADDING):
            self.__btn_add.show()
        else:
            self.__btn_add.hide()


    def set_playing(self, value):
    
        if (value):
            self.__btn_play.hide()
            self.__btn_pause.show()
        else:
            self.__btn_pause.hide()
            self.__btn_play.show()


    def set_title(self, title):

        self.__progress.set_title(title)
        self.__tuner.set_title(title)


    def set_position(self, pos, total):
    
        self.__progress.set_position(pos, total)
        self.__tuner.set_position(pos, total)


    def set_value(self, value, unit):
    
        self.__tuner.set_value(value, unit)
        
