from com import Component, msgs

from AVDevice import AVDevice
from MediaRenderer import MediaRenderer


class UPnPAVFactory(Component):
    """
    Factory component for creating UPnP AV storage devices.
    This component monitors SSDP events and creates/removes devices accordingly.
    """

    def __init__(self):
    
        self.__dev_ids = {}
        self.__dev_names = {}
        Component.__init__(self)
       
        
        
    def handle_SSDP_EV_DEVICE_DISCOVERED(self, uuid, descr):

        device_type = descr.get_device_type()
        print "UPnP device appeared:", uuid, descr.get_friendly_name()

        if (device_type in AVDevice.DEVICE_TYPES):
            device = AVDevice(descr)
            dev_id = device.get_device_id()
            self.__dev_ids[uuid] = dev_id
            self.__dev_names[uuid] = descr.get_friendly_name()
            self.emit_message(msgs.CORE_EV_DEVICE_ADDED, dev_id, device)
            
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              u"Discovered network storage \xbb%s\xab" \
                              %  descr.get_friendly_name())

        elif (device_type in MediaRenderer.DEVICE_TYPES):
            device = MediaRenderer(descr)
            self.emit_message(msgs.MEDIA_EV_OUTPUT_ADDED, device)
            
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              u"Discovered media renderer \xbb%s\xab" \
                              %  descr.get_friendly_name())


    def handle_SSDP_EV_DEVICE_GONE(self, uuid):

        dev_id = self.__dev_ids.get(uuid)
        print "UPnP device disappeared:", uuid
        if (dev_id):
            name = self.__dev_names[uuid]
            self.emit_message(msgs.CORE_EV_DEVICE_REMOVED, dev_id)
            del self.__dev_ids[uuid]
            del self.__dev_names[uuid]

            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              u"Network storage \xbb%s\xab is gone" \
                              % name)

