from com import Component, msgs
from upnp import ssdp
from utils.MiniXML import MiniXML
from io import Downloader
from upnp.DeviceDescription import DeviceDescription
from utils import logging
from utils import network

import gobject
import threading
import socket
import select


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

    
        Component.__init__(self)
            
            
    def __start_discovery(self):
    
        t = threading.Thread(target = self.__discovery_thread)
        t.setDaemon(True)
        t.start()
            

    def __discovery_thread(self):
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        for i in range(3):
            ssdp.broadcast_msearch(sock)
            while (True):
                r_socks, w_socks, x_socks = select.select([sock], [], [], 6)
                if (r_socks):
                    # process response
                    r_sock = r_socks[0]
                    data, addr = r_sock.recvfrom(1024)
                    
                    if (not "\r\n\r\n" in data):
                        continue
                    
                    headers = network.HTTPHeaders(data)
                    
                    if (headers.http_type == headers.TYPE_INVALID or
                          headers.status != 200):
                        continue
                    
                    # ignore MediaBox from the same IP (i.e. myself)
                    if (headers["X-MEDIABOX-IGNORE"] == network.get_ip()):
                        continue
                    
                    uuid = headers["USN"]
                    location = headers["LOCATION"]
                    max_age = ssdp.parse_max_age(headers["CACHE-CONTROL"])
                    
                    gobject.timeout_add(0, self.__handle_ssdp_alive,
                                        uuid, location, max_age)
                    
                else:
                    # timeout
                    break
            #end while
        #end for
        print "FINISHED DISCOVERING"
        

    def __on_expire(self, uuid):
        """
        Timer for removing UPnP devices that expire.
        """
        
        logging.debug("UPnP device [%s] has expired", uuid)
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
                self.emit_message(msgs.SSDP_EV_DEVICE_DISCOVERED, uuid, descr)
            #end if
        #end if
        

    """
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
    """
    
    
    def __parse_subscription(self, req):

        callback = req.get_header("CALLBACK")
        nt = req.get_header("NT")
        sid = req.get_header("SID")
        timeout = req.get_header("TIMEOUT") or "Second-1800"
        
    

    def __handle_ssdp_alive(self, uuid, location, max_age):
    
        logging.debug("UPnP device %s is ALIVE, max-age %ds", uuid, max_age)
        if (not uuid in self.__servers and
                not uuid in self.__processing):
            self.__servers[uuid] = location
            self.__processing[uuid] = location

            Downloader(location,
                        self.__on_receive_description_xml,
                        location, uuid, [""])
        #end if
                        
        # set up expiration handler
        if (uuid in self.__expiration_handlers):
            logging.debug("UPnP device [%s] is still ALIVE", uuid)
            print "got ALIVE from", uuid
            gobject.source_remove(self.__expiration_handlers[uuid])
            
        print uuid, "will expire in", max_age, "seconds"
        self.__expiration_handlers[uuid] = gobject.timeout_add(
                    max_age * 1000, self.__on_expire, uuid)


    def __handle_ssdp_byebye(self, uuid):
    
        logging.debug("UPnP device %s is GONE", uuid)
        if (uuid in self.__servers):
            del self.__servers[uuid]
            if (uuid in self.__processing):
                del self.__processing[uuid]
            self.emit_message(msgs.SSDP_EV_DEVICE_GONE, uuid)


    def handle_COM_EV_APP_STARTED(self):
    
        error = self.emit_message(msgs.HTTPSERVER_SVC_BIND_UDP,
                                  self, ssdp.SSDP_IP, ssdp.SSDP_PORT)
        self.__start_discovery()
        
        
        
    def handle_HTTPSERVER_EV_REQUEST(self, owner, req):
    
        if (owner != self): return
        
        method = req.get_method()
        if (method == "M-SEARCH"):
            self.emit_message(msgs.SSDP_EV_MSEARCH, req)
                        
        elif (method == "NOTIFY"):        
            if (req.get_header("X-MEDIABOX-IGNORE") == network.get_ip()):
                return
                
            max_age = ssdp.parse_max_age(req.get_header("CACHE-CONTROL"))
            location = req.get_header("LOCATION")
            usn = req.get_header("USN")
            nts = req.get_header("NTS")
            if ("::" in usn):
                uuid, urn = usn.split("::")
            else:
                uuid = usn
                urn = ""

            if (nts == "ssdp:alive"):
                self.__handle_ssdp_alive(uuid, location, max_age)

            elif (nts == "ssdp:byebye"):
                self.__handle_ssdp_byebye(uuid)


    def handle_SSDP_ACT_SEARCH_DEVICES(self):
    
        self.__start_discovery()

