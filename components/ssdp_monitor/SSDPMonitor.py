from com import Component, msgs
from upnp import ssdp
from utils.MiniXML import MiniXML
from utils.Downloader import Downloader
from upnp.DeviceDescription import DeviceDescription
from utils import logging

import gobject


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"


class SSDPMonitor(Component):
    """
    Component for monitoring the presence of UPnP devices.
    """

    def __init__(self):
    
        # table: UUID -> location
        self.__servers = {}
        
        # table of the devices currently being processed: UUID -> location
        self.__processing = {}

        self.__monitoring = False
        self.__discovery_monitor = None
        self.__idle_timer = 0
    
        Component.__init__(self)


    def handle_event(self, event, *args):
    
        # anything happened - wake up!
        if (not self.__monitoring):
            logging.info("SSDP Monitor waking up")
            nsock, dsock = ssdp.open_sockets()
            gobject.timeout_add(0, self.__discovery_chain, dsock, 0)
            gobject.io_add_watch(nsock, gobject.IO_IN, self.__check_ssdp)
            self.__discovery_monitor = gobject.io_add_watch(dsock, gobject.IO_IN, self.__check_ssdp)            
            self.__monitoring = True
            

    def __discovery_chain(self, sock, i):
    
        if (i == 0):
            ssdp.discover_devices()
            gobject.timeout_add(3000, self.__discovery_chain, sock, i + 1)
        elif (i == 1):
            ssdp.discover_devices()
            gobject.timeout_add(3000, self.__discovery_chain, sock, i + 1)
        elif (i == 2):
            gobject.source_remove(self.__discovery_monitor)
            sock.close()
            

    def __on_receive_description_xml(self, cmd, *args):
        """
        Callback for checking the given UPnP device by parsing its
        description XML. Announces the availability of new devices.
        """

        if (cmd == Downloader().DOWNLOAD_FINISHED):
            location, xml, uuid = args

            # if the device is not in the processing table, it has said
            # "bye bye" while processing the initialization; in that case
            # simply ignore it
            if (not uuid in self.__processing):
                return
    
            del self.__processing[uuid]
    
            dom = MiniXML(xml, _NS_DESCR).get_dom()
            descr = DeviceDescription(location, dom)
            
            # announce availability of device
            logging.info("discovered UPnP device [%s] of type [%s]" \
                         % (descr.get_friendly_name(), descr.get_device_type()))
            logging.debug("propagating availability of device [%s]" % uuid)
            self.emit_event(msgs.SSDP_EV_DEVICE_DISCOVERED, uuid, descr)            


    def __check_ssdp(self, sock, cond):
    
        ssdp_event = ssdp.poll_event(sock)
        if (ssdp_event):
            event, location, usn = ssdp_event
            if ("::" in usn):
                uuid, urn = usn.split("::")
            else:
                uuid = usn
                urn = ""

            if (event == ssdp.SSDP_ALIVE):
                logging.debug("UPnP device %s is ALIVE", uuid)
                if (not uuid in self.__servers and
                      not uuid in self.__processing):
                    self.__servers[uuid] = location
                    self.__processing[uuid] = location

                    Downloader().get_async(location,
                                           self.__on_receive_description_xml,
                                           uuid)

            elif (event == ssdp.SSDP_BYEBYE):
                logging.debug("UPnP device %s is GONE", uuid)
                if (uuid in self.__servers):
                    del self.__servers[uuid]
                    if (uuid in self.__processing):
                        del self.__processing[uuid]
                    self.emit_event(msgs.SSDP_EV_DEVICE_GONE, uuid)
            #end if

        #end if
        
        return True

