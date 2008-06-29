from com import Component, events

from AVDevice import AVDevice
from BinaryLight import BinaryLight


class UPnPDeviceFactory(Component):

    def __init__(self):
    
        Component.__init__(self)
       
        

    def handle_event(self, ev, *args):
    
        if (ev == events.SSDP_EV_DEVICE_DISCOVERED):
            uuid, device_type, location, descr = args

            if (device_type in AVDevice.DEVICE_TYPES):
                device = AVDevice(location, descr)
                self.emit_event(events.CORE_EV_DEVICE_ADDED, uuid, device)


        elif (ev == events.SSDP_EV_DEVICE_GONE):
            uuid = args[0]
            # TODO: don't emit this event when the device isn't a AV device
            self.emit_event(events.CORE_EV_DEVICE_REMOVED, uuid)

