from utils.Observable import Observable
from ui.Dialog import Dialog
from mediabox.FMRadio import *
import maemostations


class FMRadioBackend(Observable):

    OBS_STATION_NAME = 0
    OBS_FREQUENCY = 1
    OBS_RADIO_ON = 2
    OBS_RADIO_OFF = 3
    
    OBS_ADD_STATION = 4
    OBS_REMOVE_STATION = 5
    
    
    def __init__(self):
    
        self.__radio = None
        self.__current_freq = 0
        self.__stations = []

        stations = maemostations.get_stations()
        for f,n in stations:
            self.__stations.append((f, n))
        
        
    def __scan_cb(self, freq):

        self.update_observer(self.OBS_STATION_NAME, "")
        self.update_observer(self.OBS_FREQUENCY, freq)
        
        
    def __radio_on(self):
    
        try:
            self.__radio = FMRadio()
            self.__radio.set_volume(50)
            if (self.__current_freq > 0):
                self.__radio.set_frequency(self.__current_freq)
            self.update_observer(self.OBS_RADIO_ON)
        except FMRadioUnavailableError:
            self.__radio = None
        
        
    def __radio_off(self):
    
        if (self.__radio):
            self.__radio.close()
        self.__radio = None
        self.update_observer(self.OBS_RADIO_OFF)


    def __tune(self, freq):
    
        if (not self.is_playing()):
            self.__radio_on()
        if (self.__radio):
            self.__radio.set_frequency(freq)
            self.__current_freq = freq
            self.update_observer(self.OBS_FREQUENCY, freq)
            self.update_observer(self.OBS_STATION_NAME, "")


    def shutdown(self):
    
        self.__radio_off()


    def get_stations(self):
    
        return self.__stations
        
        
    def add_station(self):
        
        dlg = Dialog()
        dlg.add_entry("Name of Station:")
        values = dlg.wait_for_values()
        if (values and self.is_playing()):
            name = values[0]
            freq = self.__radio.get_frequency()
            self.__stations.append((freq, name))
            maemostations.save_stations(self.__stations)
            self.update_observer(self.OBS_ADD_STATION, freq, name)
         
        
        
    def remove_station(self, index):
    
        del self.__stations[index]
        maemostations.save_stations(self.__stations)
        self.update_observer(self.OBS_REMOVE_STATION, index)
        
    def set_station(self, index):
    
        freq, name = self.__stations[index]
        self.__tune(freq)
        self.update_observer(self.OBS_STATION_NAME, name)


    def get_frequency_range(self):
    
        low, high = self.__radio.get_frequency_range()
        return (low, high)


    def tune(self, percent):
    
        if (not self.is_playing()):
            self.__radio_on()
        low, high = self.__radio.get_frequency_range()
        width = high - low
        freq = int(low + width * (percent / 100.0))

        self.__tune(freq)


    def set_position(self, percent):
    
        low, high = self.__radio.get_frequency_range()
        width = high - low
        
        freq = int(low + width * (percent / 100.0))
        self.__tune(freq)
        

    def is_playing(self):
    
        return (self.__radio != None)
        
        
    def play_pause(self):
    
        if (not self.is_playing()):
            self.__radio_on()
        else:
            self.__radio_off()
            
    def next(self):
    
        if (self.__radio):
            freq = self.__radio.scan_next(self.__scan_cb)
            self.__current_freq = freq
            
            
    def previous(self):
    
        if (self.__radio):
            freq = self.__radio.scan_previous(self.__scan_cb)
            self.__current_freq = freq


    def set_volume(self, volume):
    
        self.__radio.set_volume(volume)
        
