from com import Viewer, msgs
from FMRadio import *
import maemostations
from StationItem import StationItem
from mediabox.TrackList import TrackList
from ui.ImageButton import ImageButton
from ui.Dialog import Dialog
from ui import dialogs
from mediabox import viewmodes
from utils import logging
import theme

import gtk


class FMRadioViewer(Viewer):

    ICON = theme.fmradio_viewer_radio
    ICON_ACTIVE = theme.fmradio_viewer_radio_active
    PRIORITY = 25

    def __init__(self):
    
        self.__stations = []
    
        self.__radio = None
        self.__volume = 50
        self.__current_freq = 0
    
        Viewer.__init__(self)
        self.__list = TrackList(with_drag_sort = True)
        self.__list.connect_button_clicked(self.__on_item_button)
        self.__list.connect_items_swapped(self.__on_swap)
        self.__list.set_geometry(10, 0, 780, 370)
        self.add(self.__list)


        # toolbar
        self.__toolbar = []
        for icon1, icon2, action in [
          (theme.btn_play_1, theme.btn_play_2, self.__play),
          (theme.btn_previous_1, theme.btn_previous_2, self.__previous),
          (theme.btn_next_1, theme.btn_next_2, self.__next),
          (theme.btn_add_1, theme.btn_add_2, self.__add_current_station)
          ]:
            btn = ImageButton(icon1, icon2)
            btn.connect_clicked(action)
            self.__toolbar.append(btn)
        #end for
        
        self.set_toolbar(self.__toolbar)
        
        
    def render_this(self):
    
        if (not self.__stations):
            self.__load_stations()
        
        
    def handle_event(self, msg, *args):
    
        if (self.is_active()):
            if (msg == msgs.HWKEY_EV_INCREMENT):
                self.__set_volume(self.__volume + 5)

            elif (msg == msgs.HWKEY_EV_DECREMENT):
                self.__set_volume(self.__volume - 5)

            # provide search-as-you-type
            elif (msg == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)           


    def __radio_on(self):
    
        #if (not Headset().is_connected()):
        #    self.update_observer(self.OBS_WARNING,
        #                         "Please connect headphones!\n"
        #                         "The FM radio only works if you connect\n"
        #                         "a headphones cable as antenna.")

        try:
            self.__radio = FMRadio()
            self.__radio.set_volume(self.__volume)
            if (self.__current_freq > 0):
                self.__radio.set_frequency(self.__current_freq)
            #self.emit_event(msgs.FMRADIO_EV_ON)
            
        except FMRadioUnavailableError:
            logging.error("FM radio is not available")
            self.__radio = None

        if (self.__radio):
            self.__toolbar[0].set_images(theme.btn_pause_1,
                                         theme.btn_pause_2)    
        
    def __radio_off(self):
    
        if (self.__radio):
            self.__radio.close()
        self.__radio = None
        #self.emit_event(msgs.FMRADIO_EV_OFF)

        self.__toolbar[0].set_images(theme.btn_play_1,
                                     theme.btn_play_2)    



    def __tune(self, freq):
    
        if (not self.__radio):
            self.__radio_on()
            
        if (self.__radio):
            self.__radio.set_frequency(freq)
            self.__current_freq = freq
            #self.update_observer(self.OBS_LOCATION, freq)
            #self.emit_event(msgs.FMRADIO_EV_TUNED, freq)


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


    def __remove_station(self, idx):
        """
        Removes the given station.
        """
    
        del self.__stations[idx]
        self.__list.remove_item(idx)
        self.__save_stations()
    

        
    def __scan_cb(self, freq, is_good):

        self.set_title("... scanning ...")
        self.set_info(self.__format_freq(freq))
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
            self.__stations.append((freq, name))
            self.__save_stations()
            self.__add_station(freq, name)
        
        
    def __play(self):
    
        if (not self.__radio):
            self.__radio_on()            
        else:
            self.__radio_off()
            
    def __next(self):
    
        if (self.__radio):
            freq = self.__radio.scan_next(self.__scan_cb)
            self.__current_freq = freq
            
            
    def __previous(self):
    
        if (self.__radio):
            freq = self.__radio.scan_previous(self.__scan_cb)
            self.__current_freq = freq


    def __set_volume(self, volume):
    
        volume = max(0, min(100, volume))
        if (self.__radio):
            self.__radio.set_volume(volume)
        self.__volume = volume


    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)


    def __search(self, key):
    
        idx = 0
        for freq, name in self.__stations:
            if (key in name.lower()):
                self.__list.scroll_to_item(idx + 1)
                logging.info("search: found '%s' for '%s'" % (name, key))
                break
            idx += 1
        #end for

