from com import Component, events
from UPnPDevice import UPnPDevice
from upnp import ssdp
from utils import logging
from utils import threads

import gobject


_SCHEMA_CONTENT_DIRECTORY = "urn:schemas-upnp-org:service:ContentDirectory:1"


class SSDPMonitor(Component):
    """
    Component for monitoring the presence of UPnP devices.
    """

    def __init__(self):
    
        # table: UUID -> location
        self.__servers = {}

        self.__monitor_timer = None
        self.__idle_timer = 0
    
        Component.__init__(self)
        

    def handle_event(self, event, *args):
    
        # anything happened - wake up!
        if (not self.__monitor_timer):
            logging.info("SSDP Monitor waking up")
            self.__monitor_timer = gobject.timeout_add(1000, self.__check_ssdp)
            
        self.__idle_timer = 0
            
            
    def __initialize_device(self, uuid, location):

        device = UPnPDevice(location)
        threads.run_unthreaded(self.emit_event,
                            events.CORE_EV_DEVICE_ADDED, uuid, device)

        
            
            
    def __check_ssdp(self):
    
        self.__idle_timer += 1
        
        ssdp_event = ssdp.poll_event()
        if (ssdp_event):
            event, location, usn = ssdp_event
            logging.debug("SSDP event: type %s, location %s, usn %s",
                          event, location, usn)
            if ("::" in usn):
                uuid, urn = usn.split("::")
            else:
                uuid = usn
                urn = ""

            if (urn == _SCHEMA_CONTENT_DIRECTORY or urn == "upnp:rootdevice"):
                if (event == ssdp.SSDP_ALIVE):
                    logging.info("UPnP device %s is ALIVE", uuid)
                    if (not uuid in self.__servers):
                        self.__servers[uuid] = location
                        threads.run_threaded(self.__initialize_device,
                                          uuid, location)
                        #device = UPnPDevice(location)
                        #self.emit_event(events.CORE_EV_DEVICE_ADDED, uuid, device)

                elif (event == ssdp.SSDP_BYEBYE):
                    logging.info("UPnP device %s is GONE", uuid)
                    if (uuid in self.__servers):
                        del self.__servers[uuid]
                        self.emit_event(events.CORE_EV_DEVICE_REMOVED, uuid)
                #end if
            #end if
        #end if
        
        if (self.__idle_timer < 10000):
            return True
        else:
            self.__monitor_timer = None
            logging.info("SSDP Monitor gone sleeping to save battery")
            return False

