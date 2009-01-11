from com import Component, msgs

from AVDevice import AVDevice


class UPnPAVFactory(Component):

    def __init__(self):
    
        self.__dev_ids = {}
        Component.__init__(self)
       
        

    def handle_message(self, ev, *args):
    
        if (ev == msgs.SSDP_EV_DEVICE_DISCOVERED):
            uuid, descr = args

            device_type = descr.get_device_type()

            if (device_type in AVDevice.DEVICE_TYPES):
                device = AVDevice(descr)
                dev_id = device.get_device_id()
                self.__dev_ids[uuid] = dev_id
                self.emit_event(msgs.CORE_EV_DEVICE_ADDED, uuid, device)
                
                self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                                   u"discovered network storage \xbb%s\xab" \
                                   %  descr.get_friendly_name())


        elif (ev == msgs.SSDP_EV_DEVICE_GONE):
            uuid = args[0]
            dev_id = self.__dev_ids.get(uuid)
            if (dev_id):
                self.emit_event(msgs.CORE_EV_DEVICE_REMOVED, dev_id)
                del self.__dev_ids[uuid]

