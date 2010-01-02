from storage import Device, File
from com import msgs
import inetstations
from utils import logging
from utils import urlquote
from ui.Dialog import Dialog
from theme import theme

import urllib


_SHOUTCAST_BASE = "http://www.shoutcast.com"


class IRadioStorage(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO


    def __init__(self):

        # genre list
        self.__genres = []
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
    
        return "iradio-stations://"
        
        
    def get_name(self):
    
        return "Internet Radio Stations"


    def get_icon(self):
    
        return theme.iradio_device


    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        f.info = "Editable list of radio stations"
        f.icon = self.get_icon()
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                         f.ITEMS_ADDABLE | \
                         f.ITEMS_DELETABLE

        return f


    def get_file(self, path):
    
        try:
            name, location = self.__decode_path(path)
        except:
            logging.error("error decoding iradio path: %s\n%s",
                          path, logging.stacktrace())
            return None

        f = File(self)
        f.name = name
        f.info = location
        f.path = path
        f.resource = location
        if (location.endswith(".ram") or location.endswith(".rm")):
            f.mimetype = "application/vnd.rn-realmedia"
        else:
            f.mimetype = "audio/x-unknown"
        f.icon = theme.iradio_device
        
        return f
        
        
    def get_contents(self, folder, begin_at, end_at, cb, *args):

        if (end_at == 0):
            end_at = 999999999
    
        cnt = 0
        for location, name in inetstations.get_stations():
            if (begin_at <= cnt <= end_at):
                f = File(self)
                f.name = name
                f.info = location
                f.path = self.__encode_path(name, location)
                f.resource = location
                if (location.endswith(".ram") or location.endswith(".rm")):
                    f.mimetype = "application/vnd.rn-realmedia"
                else:
                    f.mimetype = "audio/x-unknown"
                f.icon = theme.iradio_device
                
                cb(f, *args)
            #end if
            cnt += 1
        #end for
        cb(None, *args)


    def new_file(self, path):
    
        # present search dialog
        dlg = Dialog()
        dlg.add_entry("Name:", "")
        dlg.add_entry("Location:", "http://")
        values = dlg.wait_for_values()
        
        if (values):
            name, location = values
            stations = inetstations.get_stations()
            stations.append((location, name))
            inetstations.save_stations(stations)
        
            item = File(self)
            item.path = self.__encode_path(name, location)
            item.resource = location
            item.name = name
            item.info = location
            if (location.endswith(".ram") or location.endswith(".rm")):
                item.mimetype = "application/vnd.rn-realmedia"
            else:
                item.mimetype = "audio/x-unknown"
            
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())
            return item

        else:
            return None


    def delete_file(self, folder, idx):
    
        stations = inetstations.get_stations()
        del stations[idx]
        inetstations.save_stations(stations)
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())




    def __encode_path(self, name, resource):
    
        path = "/" + "\t\t\t".join([name, resource])
        return urlquote.quote(path)


    def __decode_path(self, path):
    
        data = urlquote.unquote(path[1:])
        name, resource = data.split("\t\t\t")
        return (name, resource)
