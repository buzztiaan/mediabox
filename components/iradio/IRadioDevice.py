from com import msgs
from storage import Device, File
from ui.dialog import InputDialog
import inetstations
from theme import theme


class IRadioDevice(Device):
    """
    Storage device for custom internet radio stations.
    """

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO


    def __init__(self):
    
        self.__stations = inetstations.get_stations()
    
        Device.__init__(self)
        
        
    def get_prefix(self):
    
        return "iradio://"
        
        
    def get_name(self):
    
        return "Internet Radio"


    def get_icon(self):
    
        return theme.mb_folder_audio


    def __make_station(self, name, url):
    
        f = File(self)
        f.name = name
        f.info = url
        f.path = File.pack_path("/", name, url)
        f.resource = url
        if (url.endswith(".ram") or url.endswith(".rm")):
            f.mimetype = "application/vnd.rn-realmedia"
        else:
            f.mimetype = "audio/x-unknown"
        
        return f


    def get_file(self, path):
    
        f = None
        print "GET FILE", path
        if (path == "/"):
            f = File(self)
            f.name = "Internet Radio"
            f.info = "Listen to Internet Radio"
            f.mimetype = File.DEVICE_ROOT
            f.icon = self.get_icon().get_path()
            f.folder_flags = File.ITEMS_ADDABLE | File.ITEMS_SORTABLE
            
        else:
            prefix, name, url = File.unpack_path(path)
            f = self.__make_station(name, url)
            
        return f


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        items = []
        for url, name in self.__stations:
            f = self.__make_station(name, url)
            items.append(f)
        #end for

        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)


    def shift_file(self, folder, pos, amount):
    
        item = self.__stations.pop(pos)
        self.__stations.insert(pos + amount, item)
        inetstations.save_stations(self.__stations)


    def new_file(self, folder):
    
        dlg = InputDialog("New Radio Station")
        dlg.add_input("Name", "New Station")
        dlg.add_input("Location", "http://")
        
        if (dlg.run() == dlg.RETURN_OK):
            name, url = dlg.get_values()
            self.__stations.append((url, name))
            inetstations.save_stations(self.__stations)
            
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
        #end if

