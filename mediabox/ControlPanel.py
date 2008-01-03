from Panel import Panel
from ui.ImageButton import ImageButton
from ui.Label import Label
from ui.ProgressBar import ProgressBar

import panel_actions
import theme
import caps

import gtk
import pango


class ControlPanel(Panel):   

    def __init__(self, esens):
    
        self.__event_sensor = esens
        self.__items = []
        self.__all_items = []
        
    
        Panel.__init__(self, esens)
        
        self.__btn_play = self.__add_button(theme.btn_play_1,
                                            theme.btn_play_2,
                      lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))

        self.__btn_record = self.__add_button(theme.btn_record_1,
                                              theme.btn_record_2,
                      lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))

        self.__progress = ProgressBar(esens)
        self.__progress.connect(self.__progress.EVENT_BUTTON_RELEASE,
                                self.__on_set_position)
        self.add(self.__progress)
        self.__all_items.append(self.__progress)

        self.__tuner = ProgressBar(esens)
        self.__tuner.connect(self.__progress.EVENT_BUTTON_RELEASE,
                            self.__on_tune)
        self.add(self.__tuner)
        self.__all_items.append(self.__tuner)

        self.__btn_previous = self.__add_button(theme.btn_previous_1,
                                                theme.btn_previous_2,
                        lambda x,y:self.update_observer(panel_actions.PREVIOUS))

        self.__btn_next = self.__add_button(theme.btn_next_1,
                                            theme.btn_next_2,
                            lambda x,y:self.update_observer(panel_actions.NEXT))

        self.__btn_add = self.__add_button(theme.btn_add_1,
                                           theme.btn_add_2,
                             lambda x,y:self.update_observer(panel_actions.ADD))


    def __add_button(self, icon, icon_active, cb):
    
        btn = ImageButton(self.__event_sensor, icon, icon_active)
        btn.connect(self.EVENT_BUTTON_RELEASE, cb)
        btn.set_visible(False)
        self.add(btn)
        self.__all_items.append(btn)

        return btn


    def __on_set_position(self, px, py):
    
        w, h = self.__progress.get_size()
        pos = max(0, min(99.9, px / float(w) * 100))
        self.update_observer(panel_actions.SET_POSITION, pos)
        
        
    def __on_tune(self, px, py):

        w, h = self.__tuner.get_size()
        pos = max(0, min(99.9, px / float(w) * 100))
        self.update_observer(panel_actions.TUNE, pos)    
    
                
        
    def set_capabilities(self, capabilities):

        for item in self.__all_items:
            item.set_visible(False)
    
        self.__items = []
        if (capabilities & caps.PLAYING):
            self.__items.append(self.__btn_play)

        if (capabilities & caps.POSITIONING):
            self.__items.append(self.__progress)

        if (capabilities & caps.TUNING):
            self.__items.append(self.__tuner)

        if (capabilities & caps.SKIPPING):
            self.__items.append(self.__btn_previous)
            self.__items.append(self.__btn_next)
                        
        if (capabilities & caps.RECORDING):
            self.__items.append(self.__btn_record)
            
        if (capabilities & caps.ADDING):
            self.__items.append(self.__btn_add)        

        w, h = self.get_size()
        
        width = 0
        for item in self.__items:
            width += item.get_size()[0]
        
        x = w - width - 10
        for item in self.__items:
            nil, y = item.get_pos()
            item.set_pos(x, y)
            item.set_visible(True)
            x += item.get_size()[0]
        
        self.render()


    def set_playing(self, value):
    
        if (value):
            self.__btn_play.set_images(theme.btn_pause_1, theme.btn_pause_2)
        else:
            self.__btn_play.set_images(theme.btn_play_1, theme.btn_play_2)


    def set_title(self, title):

        self.__progress.set_title(title)
        self.__tuner.set_title(title)


    def set_position(self, pos, total):
    
        self.__progress.set_position(pos, total)
        #self.__tuner.set_position(pos, total)


    def set_value(self, value, unit):
    
        self.__tuner.set_value(value, unit)
        
