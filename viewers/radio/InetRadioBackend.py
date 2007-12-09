from utils.Observable import Observable
from ui.Dialog import Dialog
from mediabox.MPlayer import MPlayer
import inetstations


class InetRadioBackend(Observable):

    OBS_STATION_NAME = 0
    OBS_FREQUENCY = 1
    
    
    def __init__(self):
    
        self.__mplayer = MPlayer()
        self.__mplayer.add_observer(self.__on_observe_mplayer)
        self.__context_id = 0
        
        self.__stations = []

        stations = inetstations.get_stations()
        for l,n in stations:
            self.__stations.append((l, n))
        

    def __on_observe_mplayer(self, src, cmd, *args):
    
        #if (not self.is_active()): return        
    
        if (cmd == src.OBS_STARTED):
            print "Started MPlayer"
            #self.update_observer(self.OBS_STATE_PAUSED)            
            
        elif (cmd == src.OBS_KILLED):
            #self.__current_uri = ""
            print "Killed MPlayer"
            #self.set_title("")
            #self.__list.hilight(-1)
            #self.update_observer(self.OBS_STATE_PAUSED)           
            
        elif (cmd == src.OBS_PLAYING):
            print "Playing"
            #self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            #self.__current_uri = ""
            print "Stopped"            
            ##self.__next_track()
            #self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            #ctx, pos, total = args
            #if (ctx == self.__context_id and self.is_active()):
            #    #print "%d / %d" % (pos, total)
            #    self.update_observer(self.OBS_POSITION, pos, total)
            pass
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):
                #self.__current_uri = ""        
                print "End of Track"
                #self.set_title("")
                #self.update_observer(self.OBS_STATE_PAUSED)
                #self.__next_track()
        

    def __tune(self, location):
    
        self.__mplayer.set_window(-1)
        self.__mplayer.set_options("")
        
        try:
            self.__context_id = self.__mplayer.load(location)
        except:
            pass


    def get_stations(self):
    
        return self.__stations
        
        
    def add_station(self):
    
        dlg = Dialog()
        dlg.add_entry("Name of Station:")
        dlg.add_entry("Location:", "http://")
        values = dlg.wait_for_values()
        if (values):
            name, location = values    
            self.__stations.append((location, name))
            inetstations.save_stations(self.__stations)
        
        
    def remove_station(self, index):
    
        del self.__stations[index]
        maemostations.save_stations(self.__stations)
        
        
    def set_station(self, index):
            
        location, name = self.__stations[index]
        self.__tune(location)
        self.update_observer(self.OBS_STATION_NAME, name)


    def set_position(self, percent):
    
        return
        

    def is_playing(self):
    
        return self.__mplayer.is_playing()
        
        
    def play_pause(self):
    
        self.__mplayer.pause()                


    def set_volume(self, volume):
    
        self.__mplayer.set_volume(volume)
        
