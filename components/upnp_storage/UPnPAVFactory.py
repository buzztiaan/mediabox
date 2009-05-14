from com import Component, msgs

from AVDevice import AVDevice


class UPnPAVFactory(Component):

    def __init__(self):
    
        self.__dev_ids = {}
        Component.__init__(self)
       
        
        
    def handle_SSDP_EV_DEVICE_DISCOVERED(self, uuid, descr):

        device_type = descr.get_device_type()

        if (device_type in AVDevice.DEVICE_TYPES):
            device = AVDevice(descr)
            dev_id = device.get_device_id()
            self.__dev_ids[uuid] = dev_id
            self.emit_message(msgs.CORE_EV_DEVICE_ADDED, dev_id, device)
            print "ADDED", dev_id
            
            self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                                u"discovered network storage \xbb%s\xab" \
                                %  descr.get_friendly_name())


    def handle_SSDP_EV_DEVICE_GONE(self, uuid):

        dev_id = self.__dev_ids.get(uuid)
        if (dev_id):
            self.emit_message(msgs.CORE_EV_DEVICE_REMOVED, dev_id)
            del self.__dev_ids[uuid]

