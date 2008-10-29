from com import Component, msgs

from AVDevice import AVDevice
from BinaryLight import BinaryLight
from DimmableLight import DimmableLight


class UPnPDeviceFactory(Component):

    def __init__(self):
    
        Component.__init__(self)
       
        

    def handle_event(self, ev, *args):
    
        if (ev == msgs.SSDP_EV_DEVICE_DISCOVERED):
            uuid, descr = args

            device_type = descr.get_device_type()

            if (device_type in AVDevice.DEVICE_TYPES):
                device = AVDevice(descr)
                self.emit_event(msgs.CORE_EV_DEVICE_ADDED, uuid, device)
                
                self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                                   u"discovered network storage \xbb%s\xab" \
                                   %  descr.get_friendly_name())

            #elif (device_type in DimmableLight.DEVICE_TYPES):
            #    device = DimmableLight(descr)


        elif (ev == msgs.SSDP_EV_DEVICE_GONE):
            uuid = args[0]
            # TODO: don't emit this event when the device isn't a AV device
            self.emit_event(msgs.CORE_EV_DEVICE_REMOVED, uuid)

