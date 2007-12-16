from RadioBackend import RadioBackend
from ui.Dialog import Dialog
from ui import dialogs
from mediabox.MPlayer import MPlayer
from mediabox import caps
import inetstations


class InetRadioBackend(RadioBackend):
    
    CAPS = caps.PLAYING | caps.TUNING | caps.ADDING
    
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
            
        elif (cmd == src.OBS_KILLED):
            #self.__current_uri = ""
            print "Killed MPlayer"
            #self.set_title("")
            self.update_observer(self.OBS_TITLE, "")
            self.update_observer(self.OBS_STOP)
            
        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__show_error(err)
                self.update_observer(self.OBS_ERROR)
            
        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.update_observer(self.OBS_PLAY)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.update_observer(self.OBS_STOP)
            
        elif (cmd == src.OBS_NEW_STREAM_TRACK):
            ctx, title = args
            if (ctx == self.__context_id):
                self.update_observer(self.OBS_TITLE, title)
            
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
                dialogs.error("Disconnected", "Stream has stopped unexpectedly.")
                print "End of Track"
                self.update_observer(self.OBS_TITLE, "")
                self.update_observer(self.OBS_STOP)
                
        
        
    def __show_error(self, errcode):
    
        if (errcode == self.__mplayer.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__mplayer.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        

    def __tune(self, location):
    
        self.__mplayer.set_window(-1)
        self.__mplayer.set_options("")
        
        self.__context_id = self.__mplayer.load(location)


    def shutdown(self):
    
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
            self.update_observer(self.OBS_ADD_STATION, location, name)
            
        
    def remove_station(self, index):
    
        del self.__stations[index]
        inetstations.save_stations(self.__stations)
        self.update_observer(self.OBS_REMOVE_STATION, index)
        
        
    def set_station(self, index):
            
        location, name = self.__stations[index]
        self.__tune(location)
        self.update_observer(self.OBS_TITLE, name)


    def set_position(self, percent):
    
        pass
        
        
    def tune(self, percent):
    
        pass
        
        
    def previous(self):
    
        pass
        
        
    def next(self):
    
        pass
        

    def is_playing(self):
    
        return self.__mplayer.is_playing()
        
        
    def play_pause(self):
    
        self.__mplayer.pause()


    def set_volume(self, volume):
    
        self.__mplayer.set_volume(volume)
        
