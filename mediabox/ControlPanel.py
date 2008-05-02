from ui.Widget import Widget
from ui.HBox import HBox
from ui.ImageButton import ImageButton
from ui.Label import Label
from ui.ProgressBar import ProgressBar
from utils.Observable import Observable

import panel_actions
import theme
import caps

import gtk
import pango


class ControlPanel(Widget, Observable):   

    def __init__(self, esens):
    
        self.__event_sensor = esens
        self.__items = []
        self.__all_items = []
        
        self.__background = None
        
    
        Widget.__init__(self, esens)
        self.__box = HBox(esens)
        self.__box.set_spacing(8)
        self.__box.set_alignment(self.__box.ALIGN_RIGHT)
        self.add(self.__box)        

        self.__btn_toggle_playlist = self.__add_button(theme.btn_playlist_1,
                                                       theme.btn_playlist_2,
                 lambda x,y:self.update_observer(panel_actions.TOGGLE_PLAYLIST))

        self.__btn_toggle_albums = self.__add_button(theme.btn_albums_1,
                                                     theme.btn_albums_2,
                 lambda x,y:self.update_observer(panel_actions.TOGGLE_PLAYLIST))
        
        self.__btn_play = self.__add_button(theme.btn_play_1,
                                            theme.btn_play_2,
                      lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))

        self.__btn_record = self.__add_button(theme.btn_record_1,
                                              theme.btn_record_2,
                      lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))

        self.__btn_zoom_in = self.__add_button(theme.btn_zoom_in_1,
                                               theme.btn_zoom_in_2,
                      lambda x,y:self.update_observer(panel_actions.ZOOM_IN))
        self.__btn_zoom_out = self.__add_button(theme.btn_zoom_out_1,
                                                theme.btn_zoom_out_2,
                      lambda x,y:self.update_observer(panel_actions.ZOOM_OUT))
        self.__btn_zoom_100 = self.__add_button(theme.btn_zoom_100_1,
                                                theme.btn_zoom_100_2,
                      lambda x,y:self.update_observer(panel_actions.ZOOM_100))
        self.__btn_zoom_fit = self.__add_button(theme.btn_zoom_fit_1,
                                                theme.btn_zoom_fit_2,
                      lambda x,y:self.update_observer(panel_actions.ZOOM_FIT))

        self.__progress = ProgressBar(esens)
        self.__progress.set_visible(False)
        self.__progress.connect(self.__progress.EVENT_BUTTON_RELEASE,
                                self.__on_set_position)
        self.__box.add(self.__progress)
        self.__all_items.append(self.__progress)

        self.__tuner = ProgressBar(esens, False)
        self.__tuner.set_visible(False)
        self.__tuner.connect(self.__progress.EVENT_BUTTON_RELEASE,
                            self.__on_tune)
        self.__box.add(self.__tuner)
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


        self.__btn_speaker = self.__add_button(theme.btn_speaker_toggle_1,
                                               theme.btn_speaker_toggle_2,
                   lambda x,y:self.update_observer(panel_actions.FORCE_SPEAKER))



    def set_bg(self, bg):
    
        self.__background = bg
        self.render()


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__box.set_size(w - 20, h)
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
    
        screen.draw_frame(theme.panel, x, y, w, h, True,
                          screen.TOP | screen.BOTTOM)



    def __add_button(self, icon, icon_active, cb):
    
        btn = ImageButton(self.__event_sensor, icon, icon_active)
        btn.connect(self.EVENT_BUTTON_RELEASE, cb)
        btn.set_visible(False)
        self.__box.add(btn)
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

        if (capabilities & caps.ZOOMING):
            self.__items.append(self.__btn_zoom_in)
            self.__items.append(self.__btn_zoom_out)
            self.__items.append(self.__btn_zoom_100)
            self.__items.append(self.__btn_zoom_fit)                             

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

        if (capabilities & caps.FORCING_SPEAKER):
            self.__items.append(self.__btn_speaker)

        if (capabilities & caps.PLAYLIST):
            self.__items.append(self.__btn_toggle_playlist)
            
        if (capabilities & caps.ALBUMS):
            self.__items.append(self.__btn_toggle_albums)

        for item in self.__items:
            item.set_visible(True)
        
        #self.render()


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
        self.__tuner.set_position(pos, total)


    def set_value(self, value, unit):
    
        self.__tuner.set_value(value, unit)
        
