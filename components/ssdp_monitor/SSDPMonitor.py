from com import Component, msgs
from upnp import ssdp
from utils.MiniXML import MiniXML
from io import Downloader
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
        
        # table: UUID -> expiration_handler
        self.__expiration_handlers = {}
        
        # table of the devices currently being processed: UUID -> location
        self.__processing = {}

        self.__monitoring = False
        self.__discovery_monitor = None
    
        Component.__init__(self)


    def handle_event(self, event, *args):

        if (event == msgs.SSDP_ACT_SEARCH_DEVICES):
            # initialize monitor if needed
            if (not self.__monitoring):
                logging.info("SSDP Monitor waking up")
                nsock, dsock = ssdp.open_sockets()
                gobject.timeout_add(0, self.__discovery_chain, dsock, 0)
                gobject.io_add_watch(nsock, gobject.IO_IN, self.__check_ssdp)
                self.__discovery_monitor = gobject.io_add_watch(dsock, gobject.IO_IN, self.__check_ssdp)            
                self.__monitoring = True
            
            else:
                ssdp.discover_devices()

            

    def __discovery_chain(self, sock, i):
    
        if (i == 0):
            ssdp.discover_devices()
            gobject.timeout_add(6000, self.__discovery_chain, sock, i + 1)
        elif (i == 1):
            ssdp.discover_devices()
            gobject.timeout_add(6000, self.__discovery_chain, sock, i + 1)
        elif (i == 2):
            pass
            #gobject.source_remove(self.__discovery_monitor)
            #sock.close()


    def __on_expire(self, uuid):
        """
        Timer for removing UPnP devices that expire.
        """
        
        del self.__expiration_handlers[uuid]
        self.__handle_ssdp_byebye(uuid)
            

    def __on_receive_description_xml(self, data, a, t, location, uuid, xml):
        """
        Callback for checking the given UPnP device by parsing its
        description XML. Announces the availability of new devices.
        """

        if (data):
            xml[0] += data
        else:
            # if the device is not in the processing table, it has said
            # "bye bye" while processing the initialization; in that case
            # simply ignore it
            if (not uuid in self.__processing):
                return
    
            del self.__processing[uuid]
            
            
            if (xml[0]):
                dom = MiniXML(xml[0], _NS_DESCR).get_dom()
                descr = DeviceDescription(location, dom)
            
                # announce availability of device
                logging.info("discovered UPnP device [%s] of type [%s]" \
                             % (descr.get_friendly_name(), descr.get_device_type()))
                logging.debug("propagating availability of device [%s]" % uuid)
                self.emit_event(msgs.SSDP_EV_DEVICE_DISCOVERED, uuid, descr)
            #end if
        #end if
        

    def __check_ssdp(self, sock, cond):
    
        ssdp_event = ssdp.poll_event(sock)
        if (ssdp_event):
            event, location, usn, max_age = ssdp_event
            if ("::" in usn):
                uuid, urn = usn.split("::")
            else:
                uuid = usn
                urn = ""

            if (event == ssdp.SSDP_ALIVE):
                self.__handle_ssdp_alive(uuid, location, max_age)

            elif (event == ssdp.SSDP_BYEBYE):
                self.__handle_ssdp_byebye(uuid)

        #end if
        
        return True


    def __handle_ssdp_alive(self, uuid, location, max_age):
    
        logging.debug("UPnP device %s is ALIVE, max-age %ds", uuid, max_age)
        if (not uuid in self.__servers and
                not uuid in self.__processing):
            self.__servers[uuid] = location
            self.__processing[uuid] = location

            Downloader(location,
                        self.__on_receive_description_xml,
                        location, uuid, [""])
                        
            # set up expiration handler
            if (uuid in self.__expiration_handlers):
                gobject.source_remove(self.__expiration_handlers[uuid])
            self.__expiration_handlers[uuid] = gobject.timeout_add(
                        max_age * 1000, self.__on_expire, uuid)


    def __handle_ssdp_byebye(self, uuid):
    
        logging.debug("UPnP device %s is GONE", uuid)
        if (uuid in self.__servers):
            del self.__servers[uuid]
            if (uuid in self.__processing):
                del self.__processing[uuid]
            self.emit_event(msgs.SSDP_EV_DEVICE_GONE, uuid)

