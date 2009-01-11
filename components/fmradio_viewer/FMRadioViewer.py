from com import Viewer, msgs
from FMRadio import *
import maemostations
import config
from RadioScale import RadioScale
from StationItem import StationItem
from mediabox.TrackList import TrackList
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.ToggleButton import ToggleButton
from ui.Dialog import Dialog
from ui import dialogs
from mediabox import viewmodes
from mediabox import config as mb_config
from utils import logging
from theme import theme

import gtk


class FMRadioViewer(Viewer):

    ICON = theme.fmradio_viewer_radio
    PRIORITY = 25

    def __init__(self):
    
        self.__stations = []
    
        self.__radio = None
        self.__current_freq = 0
        

        Viewer.__init__(self)
        self.__list = TrackList(with_drag_sort = True)
        self.__list.connect_button_clicked(self.__on_item_button)
        self.__list.connect_items_swapped(self.__on_swap)
        self.__list.set_geometry(10, 0, 680, 370)
        self.add(self.__list)
        
        self.__scale = RadioScale()
        self.__scale.set_geometry(695, 5, 100, 360)
        self.__scale.set_range(87.5, 108.0)
        self.add(self.__scale)
        self.__scale.connect_tuned(self.__on_tune)


        # toolbar
        btn_play = ImageButton(theme.mb_btn_play2_1, theme.mb_btn_play2_2)
        btn_play.connect_clicked(self.__play)
        
        btn_prev = ImageButton(theme.mb_btn_previous_1, theme.mb_btn_previous_2)
        btn_prev.connect_clicked(self.__previous)

        btn_next = ImageButton(theme.mb_btn_next_1, theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__next)

        btn_add = ImageButton(theme.mb_btn_add_1, theme.mb_btn_add_2)
        btn_add.connect_clicked(self.__add_current_station)
                
        btn_speaker = ToggleButton(theme.mb_btn_speaker_off,
                                   theme.mb_btn_speaker_on)
        btn_speaker.connect_toggled(self.__toggle_speaker)

        self.__toolbar = [
            btn_play,
            Image(theme.mb_toolbar_space_1),
            btn_prev,
            btn_next,
            Image(theme.mb_toolbar_space_1),
            btn_add,
            Image(theme.mb_toolbar_space_1),
            btn_speaker
        ]
        
        self.set_toolbar(self.__toolbar)
        
        
    def render_this(self):
    
        if (not self.__stations):
            self.__load_stations()
        
        
    def handle_message(self, msg, *args):
    
        if (msg == msgs.MEDIA_ACT_STOP):
            self.__radio_off()
            
        elif (msg == msgs.CORE_EV_APP_SHUTDOWN):
            self.__radio_off()
    
        if (self.is_active()):
            if (msg == msgs.HWKEY_EV_INCREMENT):
                self.__set_volume(mb_config.volume() + 5)

            elif (msg == msgs.HWKEY_EV_DECREMENT):
                self.__set_volume(mb_config.volume() - 5)

            # provide search-as-you-type
            elif (msg == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)           


    def __set_region(self, region):
    
        regions = {"EUR": self.__radio.FM_BAND_EUR,
                   "JPN": self.__radio.FM_BAND_JPN}
    
        fm_band = regions[region]
    
        current_fm_band = self.__radio.get_fm_band()
        if (current_fm_band != fm_band):
            try:
                self.__radio.set_fm_band(fm_band)
            except:
                dialogs.warning("Not supported", "Unsupported region settings.")


    def __radio_on(self):
    
        #if (not Headset().is_connected()):
        #    self.update_observer(self.OBS_WARNING,
        #                         "Please connect headphones!\n"
        #                         "The FM radio only works if you connect\n"
        #                         "a headphones cable as antenna.")


        self.emit_event(msgs.MEDIA_ACT_STOP)
        try:
            self.__radio = FMRadio()
            self.__set_region(config.get_region())
            self.__radio.set_volume(mb_config.volume())
            if (self.__current_freq > 0):
                self.__radio.set_frequency(self.__current_freq)
            #self.emit_event(msgs.FMRADIO_EV_ON)
            
        except FMRadioUnavailableError:
            logging.error("FM radio is not available")
            self.__radio = None

        if (self.__radio):
            self.__toolbar[0].set_images(theme.mb_btn_pause2_1,
                                         theme.mb_btn_pause2_2)    
            a, b = self.__radio.get_frequency_range()
            self.__scale.set_range(a / 1000.0, b / 1000.0)
            
        
    def __radio_off(self):
    
        if (self.__radio):
            self.__radio.close()
        self.__radio = None

        self.__toolbar[0].set_images(theme.mb_btn_play2_1,
                                     theme.mb_btn_play2_2)    



    def __tune(self, freq):
    
        if (not self.__radio):
            self.__radio_on()
            
        if (self.__radio):
            self.__radio.set_frequency(freq)
            self.__current_freq = freq
            self.emit_event(msgs.MEDIA_EV_LOADED, self, None)
            self.__scale.tune(freq / 1000.0)


    def __format_freq(self, freq):
    
        return "%3.02f MHz" % (freq / 1000.0)
        
        
    def __load_stations(self):
        """
        Loads the configured radio stations.
        """
        
        try:
            stations = maemostations.get_stations()
        except:
            logging.error("could not load list of radio stations:\n%s" \
                          % logging.stacktrace())
            stations = []
            
        for freq, name in stations:
            self.__add_station(freq, name)
            
            
    def __save_stations(self):
        """
        Saves the current list of radio stations.
        """
        
        try:
            maemostations.save_stations(self.__stations)
        except:
            logging.error("could not save list of radio stations:\n%s" \
                          % logging.stacktrace())
            
            
    def __add_station(self, freq, name):
        """
        Adds a radio station.
        """
        
        self.__stations.append((freq, name))
        
        item = StationItem(self.__format_freq(freq), name)
        self.__list.append_item(item)
        self.__save_stations()


    def __remove_station(self, idx):
        """
        Removes the given station.
        """
    
        del self.__stations[idx]
        self.__list.remove_item(idx)
        self.__save_stations()
    

        
    def __scan_cb(self, freq):

        self.set_title("")
        self.set_info(self.__format_freq(freq))
        self.__scale.tune(freq / 1000.0)
        gtk.main_iteration(False)


    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            freq, name = self.__stations[idx]
            self.__tune(freq)
            self.__list.hilight(idx)
            self.set_title(name)
            
        elif (button == item.BUTTON_REMOVE):
            response = dialogs.question("Remove",
                                        "Remove this station?")
            if (response == 0):
                self.__remove_station(idx)


    def __on_tune(self, freq):
    
        self.set_title("")
        self.__list.hilight(-1)
        self.__list.render()
        self.__tune(freq * 1000)
        
        
    def __on_swap(self, idx1, idx2):
    
        tmp = self.__stations[idx1]
        self.__stations[idx1] = self.__stations[idx2]
        self.__stations[idx2] = tmp
        self.__save_stations()
        
        
    def __add_current_station(self):

        dlg = Dialog()
        dlg.add_entry("Name of Station:")
        values = dlg.wait_for_values()
        if (values and self.__radio):
            name = values[0]
            freq = self.__radio.get_frequency()
            self.__add_station(freq, name)
        
        
    def __toggle_speaker(self, value):
    
        if (value):
            self.emit_event(msgs.SYSTEM_ACT_FORCE_SPEAKER_ON)
        else:
            self.emit_event(msgs.SYSTEM_ACT_FORCE_SPEAKER_OFF)


    def __play(self):
    
        if (not self.__radio):
            self.__radio_on()            
        else:
            self.__radio_off()
            
    def __next(self):
    
        if (self.__radio):
            self.__list.hilight(-1)
            self.__list.render()
            freq = self.__radio.scan_next(self.__scan_cb)
            self.__current_freq = freq
            
            
    def __previous(self):
    
        if (self.__radio):
            self.__list.hilight(-1)
            self.__list.render()
            freq = self.__radio.scan_previous(self.__scan_cb)
            self.__current_freq = freq


    def __set_volume(self, volume):
    
        volume = max(0, min(100, volume))
        if (self.__radio):
            self.__radio.set_volume(volume)
        mb_config.set_volume(volume)
        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)


    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.NO_STRIP)


    def __search(self, key):
    
        idx = 0
        for freq, name in self.__stations:
            if (key in name.lower()):
                self.__list.scroll_to_item(idx + 1)
                logging.info("search: found '%s' for '%s'" % (name, key))
                break
            idx += 1
        #end for

