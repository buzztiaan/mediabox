from viewers.Viewer import Viewer
from RadioItem import RadioItem
from RadioThumbnail import RadioThumbnail
from FMRadioBackend import FMRadioBackend
from InetRadioBackend import InetRadioBackend
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from ui import dialogs
from mediabox import caps
import theme


import gtk
import gobject
import os


class RadioViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_radio    
    ICON_ACTIVE = theme.viewer_radio_active
    PRIORITY = 25
    BORDER_WIDTH = 0
    CAPS = caps.PLAYING | caps.SKIPPING | caps.TUNING | caps.ADDING
    IS_EXPERIMENTAL = False


    def __init__(self):
    
        # mapping: name -> radio backend
        self.__radios = {}
        
        self.__items = []
        self.__current_radio = None
        self.__volume = 50
        self.__is_on = False

        Viewer.__init__(self)                
        box = gtk.HBox()
        self.set_widget(box)

        # stations list
        self.__list = ItemList(600, 80)
        self.__list.set_background(theme.background.subpixbuf(185, 0, 600, 400))
        self.__list.set_graphics(theme.item, theme.item_active)        
        self.__list.set_font(theme.font_plain)
        self.__list.set_arrows(theme.arrows)
        self.__list.show()
                
        kscr = KineticScroller(self.__list)
        kscr.add_observer(self.__on_observe_list)
        kscr.show()
        box.pack_start(kscr, True, True, 10)                       
        
              
        # fill with items
        for name, icon, backend in [
                ("FM Radio", theme.viewer_radio_fmradio, FMRadioBackend)]:
                #("Internet Radio", theme.viewer_radio_inetradio, InetRadioBackend)]:
            item = RadioItem(name)
            tn = RadioThumbnail(icon, name)
            item.set_thumbnail(tn)
            self.__radios[name] = backend()
            self.__radios[name].add_observer(self.__on_observe_backend)
            self.__items.append(item)
        #end for
        
        self.load(self.__items[0])
        
        
    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            if (px > 520):
                idx = self.__list.get_index_at(py)
                if (idx >= 0):
                    response = dialogs.question("Remove",
                                                "Remove this station?")
                    if (response == 0):
                        self.__current_radio.remove_station(idx)
                    
            elif (px > 420):
                idx = self.__list.get_index_at(py)
                if (idx >= 0):
                    self.__current_radio.set_station(idx)                
                    self.__list.hilight(idx)


        #elif (cmd == src.OBS_TAP_AND_HOLD):
        #    px, py = args
        #    idx = self.__list.get_index_at(py)
        #    if (idx >= 0):
        #        self.__current_radio.remove_station(idx)
        #        self.__load_stations()
                    
                    
    def __on_observe_backend(self, src, cmd, *args):
    
        if (cmd == src.OBS_STATION_NAME):
            name = args[0]
            self.update_observer(self.OBS_TITLE, name)
            
        elif (cmd == src.OBS_FREQUENCY):
            freq = args[0]
            low, high = self.__current_radio.get_frequency_range()
            self.update_observer(self.OBS_POSITION, freq - low, high - low)
            self.update_observer(self.OBS_FREQUENCY_MHZ, freq / 1000.0)
            
            # this is useful during frequency scanning so that the user will
            # see the current frequency
            while (gtk.events_pending()): gtk.main_iteration()
            
        elif (cmd == src.OBS_RADIO_ON):
            self.__is_on = True
            self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_RADIO_OFF):
            self.__is_on = False
            self.update_observer(self.OBS_STATE_PAUSED)

        elif (cmd == src.OBS_ADD_STATION):
            freq, name = args
            self.__append_station(freq, name)
            
        elif (cmd == src.OBS_REMOVE_STATION):
            idx = args[0]
            self.__list.remove_item(idx)
            
            
    def __append_station(self, freq, name):

        title = name + "\n[%3.02f MHz]" % (freq / 1000.0)
        idx = self.__list.append_item(title, None)
        self.__list.overlay_image(idx, theme.btn_load, 440, 24)
        self.__list.overlay_image(idx, theme.remove, 540, 24)
        


    def __load_stations(self):
    
        self.__list.clear_items()
        for freq, name in self.__current_radio.get_stations():
            self.__append_station(freq, name)

        
    def is_available(self):
        
        # FM radio is not available on all internet tablet models
        try:
            from mediabox.FMRadio import *
            r = FMRadio()
        except FMRadioUnsupportedError:
            return False
        else:
            r.close()
            return True
        
        
    def shutdown(self):
        
        # stop radio on exit
        self.__current_radio.shutdown()
        

    def load(self, item):
    
        name = item.get_uri()
        self.__current_radio = self.__radios[name]
        self.__load_stations()
        
        

    def increment(self):
            
        self.__volume = min(100, self.__volume + 5)
        self.__current_radio.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)
        
        
    def decrement(self):

        self.__volume = max(0, self.__volume - 5)
        self.__current_radio.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)


    def tune(self, value):

        self.__list.hilight(-1)    
        self.__current_radio.tune(value)


    def play_pause(self):
    
        self.__current_radio.play_pause()

            
    def previous(self):

        self.__list.hilight(-1)    
        self.__current_radio.previous()
        
        
    def next(self):

        self.__list.hilight(-1)    
        self.__current_radio.next()


    def add(self):
    
        self.__current_radio.add_station()


    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        if (self.__is_on):
            self.update_observer(self.OBS_STATE_PLAYING)
            
           
    def hide(self):
    
        Viewer.hide(self)

