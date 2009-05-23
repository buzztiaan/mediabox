from com import msgs
from storage import Device, File
from IRadioStorage import IRadioStorage
from ShoutcastStorage import ShoutcastStorage
from theme import theme


class IRadio(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO

    def __init__(self):
        
        self.__devices = [IRadioStorage(), ShoutcastStorage()]
        
        Device.__init__(self)
        
        
    def get_icon(self):
    
        return theme.iradio_device
        
        
    def get_prefix(self):
    
        return "iradio://"
        
        
    def get_name(self):

        return "Internet Radio"

        
    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.name = self.get_name()
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.info = "Listen to internet radio stations"
        
        return f


    def get_contents(self, folder, begin_at, end_at, cb, *args):
    
        if (end_at == 0):
            end_at = 999999999
            
        cnt = 0
        for dev in self.__devices:
            if (begin_at <= cnt <= end_at):
                cb(dev.get_root(), *args)
            cnt += 1
        #end for
        cb(None, *args)


    def handle_CORE_EV_APP_STARTED(self):
    
        for dev in self.__devices:
            self.emit_message(msgs.CORE_EV_DEVICE_ADDED, dev.get_device_id(), dev)
