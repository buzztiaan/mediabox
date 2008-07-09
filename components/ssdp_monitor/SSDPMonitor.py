from com import Component, msgs
from upnp import ssdp
from upnp.MiniXML import MiniXML
from upnp.DeviceDescription import DeviceDescription
from utils import logging
from utils import threads

import urllib
import gobject


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"


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
            
            
    def __check_device(self, uuid, location):
        """
        Thread for checking the given UPnP device by retrieving and parsing its
        description XML. Announces the availability of new devices.
        """
        
        logging.debug("loading UPnP device description '%s'", location)
        xml = urllib.urlopen(location).read()
        dom = MiniXML(xml, _NS_DESCR).get_dom()

        descr = DeviceDescription(location, dom)
        logging.info("discovered UPnP device [%s] of type [%s]" \
                     % (descr.get_friendly_name(), descr.get_device_type()))

        logging.debug("propagating availability of device [%s]" % uuid)        
        threads.run_unthreaded(self.emit_event,
                               msgs.SSDP_EV_DEVICE_DISCOVERED, uuid, descr)


    def __check_ssdp(self):
    
        self.__idle_timer += 1
        
        ssdp_event = ssdp.poll_event()
        if (ssdp_event):
            event, location, usn = ssdp_event
            if ("::" in usn):
                uuid, urn = usn.split("::")
            else:
                uuid = usn
                urn = ""

            if (event == ssdp.SSDP_ALIVE):
                logging.debug("UPnP device %s is ALIVE", uuid)
                if (not uuid in self.__servers):
                    self.__servers[uuid] = location
                    threads.run_threaded(self.__check_device,
                                         uuid, location)

            elif (event == ssdp.SSDP_BYEBYE):
                logging.debug("UPnP device %s is GONE", uuid)
                if (uuid in self.__servers):
                    del self.__servers[uuid]
                    self.emit_event(msgs.SSDP_EV_DEVICE_GONE, uuid)
            #end if

        #end if
        
        if (self.__idle_timer < 10000):
            return True
        else:
            self.__monitor_timer = None
            logging.info("SSDP Monitor gone sleeping to save battery")
            return False

