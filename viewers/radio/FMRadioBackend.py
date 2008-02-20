from RadioBackend import RadioBackend
from ui.Dialog import Dialog
from mediabox.FMRadio import *
from mediabox.Headset import Headset
from mediabox import caps
import maemostations


class FMRadioBackend(RadioBackend):
        
    CAPS = caps.PLAYING | caps.SKIPPING | caps.TUNING | caps.ADDING | \
           caps.FORCING_SPEAKER
        
    def __init__(self):
    
        self.__radio = None
        self.__current_freq = 0
        self.__stations = []

        try:
            stations = maemostations.get_stations()
        except:
            stations = []
            
        for f,n in stations:
            self.__stations.append((f, n))
                   
        
    def __scan_cb(self, freq):

        self.update_observer(self.OBS_TITLE, "")
        self.update_observer(self.OBS_LOCATION, freq)
        
        
    def __radio_on(self):
    
        if (not Headset().is_connected()):
            self.update_observer(self.OBS_WARNING,
                                 "Please connect headphones!\n"
                                 "The FM radio only works if you connect\n"
                                 "a headphones cable as antenna.")
    
        try:
            self.__radio = FMRadio()
            self.__radio.set_volume(50)
            if (self.__current_freq > 0):
                self.__radio.set_frequency(self.__current_freq)
            self.update_observer(self.OBS_PLAY)
        except FMRadioUnavailableError:
            self.__radio = None
        
        
    def __radio_off(self):
    
        if (self.__radio):
            self.__radio.close()
        self.__radio = None
        self.update_observer(self.OBS_STOP)


    def __tune(self, freq):
    
        if (not self.is_playing()):
            self.__radio_on()
        if (self.__radio):
            self.__radio.set_frequency(freq)
            self.__current_freq = freq
            self.update_observer(self.OBS_LOCATION, freq)
            self.update_observer(self.OBS_TITLE, "")


    def __format_freq(self, freq):
    
        return "%3.02f MHz" % (freq / 1000.0)


    def shutdown(self):
    
        self.__radio_off()


    def get_stations(self):

        stations = [ (self.__format_freq(freq), name)
                     for freq, name in self.__stations ]

        return stations
        
        
    def add_station(self):
        
        dlg = Dialog()
        dlg.add_entry("Name of Station:")
        values = dlg.wait_for_values()
        if (values and self.is_playing()):
            name = values[0]
            freq = self.__radio.get_frequency()
            self.__stations.append((freq, name))
            maemostations.save_stations(self.__stations)
            self.update_observer(self.OBS_ADD_STATION,
                                 self.__format_freq(freq), name)
         
        
        
    def remove_station(self, index):
    
        del self.__stations[index]
        maemostations.save_stations(self.__stations)
        self.update_observer(self.OBS_REMOVE_STATION, index)
        
    def set_station(self, index):
    
        freq, name = self.__stations[index]
        self.__tune(freq)
        self.update_observer(self.OBS_TITLE, name)


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
        
        
    def stop(self):
    
        self.__radio_off()

