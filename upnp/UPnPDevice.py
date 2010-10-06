from com import Component, msgs
from upnp import ssdp
from utils import network
from utils import logging

import os
import commands



_BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_DEVICE_DESCRIPTION = """<?xml version="1.0"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <specVersion>
    <major>1</major><minor>0</minor>
  </specVersion>
  <URLBase>@@URL_BASE@@</URLBase>
  
  <device>
    <deviceType>@@DEVICE_TYPE@@</deviceType>
    <friendlyName>@@FRIENDLY_NAME@@</friendlyName>
    <manufacturer>@@MANUFACTURER@@</manufacturer>
    <manufacturerURL>@@MANUFACTURER_URL@@</manufacturerURL>
    <modelDescription>@@MODEL_DESCRIPTION@@</modelDescription>
    <modelName>@@MODEL_NAME@@</modelName>
    <modelNumber>@@MODEL_NUMBER@@</modelNumber>
    <modelURL>@@MODEL_URL@@</modelURL>
    <serialNumber>@@SERIAL@@</serialNumber>
    <UDN>@@UDN@@</UDN>
    <UPC>@@UPC@@</UPC>
    
    <iconList>
      <icon>
        <mimetype>image/png</mimetype>
        <width>64</width>
        <height>64</height>
        <depth>24</depth>
        <url>/icon.png</url>
      </icon>
    </iconList>
    
    <presentationURL></presentationURL>
  
    @@SERVICE_LIST@@

  </device>
</root>
"""

_SERVICE = """
<service>
  <serviceType>@@SERVICE_TYPE@@</serviceType>
  <serviceId>@@SERVICE_ID@@</serviceId>
  <SCPDURL>@@SCPD_URL@@</SCPDURL>
  <controlURL>@@CONTROL_URL@@</controlURL>
  <eventSubURL>@@EVENT_URL@@</eventSubURL>
</service>
"""

class UPnPDevice(Component):
    """
    Abstract base class for UPnP server devices.
    """
    
    PROP_UPNP_DEVICE_TYPE = 0
    PROP_UPNP_FRIENDLY_NAME = 1
    PROP_UPNP_MANUFACTURER = 2
    PROP_UPNP_MANUFACTURER_URL = 3
    PROP_UPNP_MODEL_DESCRIPTION = 4
    PROP_UPNP_MODEL_NAME = 5
    PROP_UPNP_MODEL_NUMBER = 6
    PROP_UPNP_MODEL_URL = 7
    PROP_UPNP_SERIAL_NUMBER = 8
    PROP_UPNP_UDN = 9
    PROP_UPNP_UPC = 10
    PROP_UPNP_SERVICE_PORT = 11
    PROP_UPNP_ICON_PATH = 12
    

    def __init__(self, *services):
    
        # services provided by the device
        self.__services = []
        
        # table: scpd_url -> service
        self.__scpd_urls = {}
        
        # table: ctrl_url -> service
        self.__ctrl_urls = {}
        
        # table: event_url -> service
        self.__event_urls = {}
    
        Component.__init__(self)
        
        for svc in services:
            self._add_service(svc)
        
        
    def _add_service(self, service):
        """
        Adds a UPnP service to this device.
        
        @param service: instance of a UPnPService
        @param ctrl_url: control URL of the service
        @param ev_url: event URL of the service
        """
    
        self.__services.append(service)
        svc_name = str(hash(service))
        scpd_url = "/scpd/%s.xml" % svc_name
        ctrl_url = "/control/%s.xml" % svc_name
        ev_url = "/event/%s.xml" % svc_name
        self.__scpd_urls[scpd_url] = service
        self.__ctrl_urls[ctrl_url] = service
        self.__event_urls[ev_url] = service


    def __get_capabilities(self):
        """
        Builds a list of the device's capabilites as (ST, USN) tuples.
        """

        # build up capabilities
        udn = self.get_prop(self.PROP_UPNP_UDN)
        dev_type = self.get_prop(self.PROP_UPNP_DEVICE_TYPE)
        
        caps = []
        caps.append(("upnp:rootdevice", udn + "::upnp:rootdevice"))
        caps.append((udn, udn))
        caps.append((dev_type, udn + "::" + dev_type))
        
        for svc in self.__services:
            svc_type = svc.get_prop(svc.PROP_UPNP_SERVICE_TYPE)
            caps.append((svc_type, udn + "::" + svc_type))

        return caps


    def __handle_msearch(self, req):
        """
        Handles M-SEARCH discovery requests.
        """

        if (req.get_header("MAN") == "\"ssdp:discover\""):
            src_host, src_port = req.get_source()
            mx = int(req.get_header("MX"))
    
            ip = network.get_ip()
            port = self.get_prop(self.PROP_UPNP_SERVICE_PORT)
            location = "http://%s:%s/Description.xml" % (ip, port)
            requested_search_target = req.get_header("ST")

            # announce capabilities
            logging.debug("[ssdp] responding to M-SEARCH")
            caps = self.__get_capabilities()
            for search_target, unique_service_name in caps:
                if (requested_search_target in ("ssdp:all", search_target)):
                    logging.debug("[ssdp] %s, %s", search_target, unique_service_name)     
                    max_age = ssdp.respond_to_msearch(src_host, src_port,
                                                      location, search_target,
                                                      unique_service_name)
                #end if
            #end for
        #end if
        

    def __handle_get(self, req):
        """
        Handles HTTP GET requests.
        """
    
        path = req.get_path()

        if (path == "/Description.xml"):
            req.send_xml(self.__make_device_description())

        elif (path == "/icon.png"):
            iconpath = self.get_prop(self.PROP_UPNP_ICON_PATH)
            if (os.path.exists(iconpath)):
                req.send_file(open(iconpath, "r"), "icon.png", "image/png")
            else:
                req.send_not_found("MediaBox", path)
           
        elif (path in self.__scpd_urls):
            svc = self.__scpd_urls[path]
            req.send_xml(svc.get_scpd())
           
        else:
            req.send_not_found("MediaBox", path)

        return True


    def __make_device_description(self):
        """
        Returns the device description in XML format.
        """

        ip = network.get_ip()
        port = self.get_prop(self.PROP_UPNP_SERVICE_PORT)
        url_base = "http://%s:%d" % (ip, port)

        service_list = "<serviceList>"
        for svc in self.__services:
            svc_name = str(hash(svc))
            scpd_url = "/scpd/%s.xml" % svc_name
            ctrl_url = "/control/%s.xml" % svc_name
            ev_url = "/event/%s.xml" % svc_name

            service_list += _SERVICE \
                            .replace("@@SERVICE_TYPE@@",
                                     svc.get_prop(svc.PROP_UPNP_SERVICE_TYPE)) \
                            .replace("@@SERVICE_ID@@",
                                     svc.get_prop(svc.PROP_UPNP_SERVICE_ID)) \
                            .replace("@@SCPD_URL@@", scpd_url) \
                            .replace("@@CONTROL_URL@@", ctrl_url) \
                            .replace("@@EVENT_URL@@", ev_url)
        #end for
        service_list += "</serviceList>"

        return _DEVICE_DESCRIPTION \
               .replace("@@URL_BASE@@", url_base) \
               .replace("@@DEVICE_TYPE@@",
                        self.get_prop(self.PROP_UPNP_DEVICE_TYPE)) \
               .replace("@@FRIENDLY_NAME@@",
                        self.get_prop(self.PROP_UPNP_FRIENDLY_NAME)) \
               .replace("@@MANUFACTURER@@",
                        self.get_prop(self.PROP_UPNP_MANUFACTURER)) \
               .replace("@@MANUFACTURER_URL@@",
                        self.get_prop(self.PROP_UPNP_MANUFACTURER_URL)) \
               .replace("@@MODEL_DESCRIPTION@@",
                        self.get_prop(self.PROP_UPNP_MODEL_DESCRIPTION)) \
               .replace("@@MODEL_NAME@@",
                        self.get_prop(self.PROP_UPNP_MODEL_NAME)) \
               .replace("@@MODEL_NUMBER@@",
                        self.get_prop(self.PROP_UPNP_MODEL_NUMBER)) \
               .replace("@@MODEL_URL@@",
                        self.get_prop(self.PROP_UPNP_MODEL_URL)) \
               .replace("@@SERIAL@@",
                        self.get_prop(self.PROP_UPNP_SERIAL_NUMBER)) \
               .replace("@@UDN@@",
                        self.get_prop(self.PROP_UPNP_UDN)) \
               .replace("@@UPC@@",
                        self.get_prop(self.PROP_UPNP_UPC)) \
               .replace("@@SERVICE_LIST@@",
                        service_list)
        
        
    def handle_COM_EV_APP_STARTED(self):

        ip = network.get_ip()
        port = self.get_prop(self.PROP_UPNP_SERVICE_PORT)
        error = self.call_service(msgs.HTTPSERVER_SVC_BIND,
                                  self, ip, port)
        if (error):
            print "Error binding to TCP"

        location = "http://%s:%d/Description.xml" % (ip, port)
        caps = self.__get_capabilities()
        for notification_type, unique_service_name in caps:
            ssdp.broadcast_alive(location, notification_type,
                                 unique_service_name)


    def handle_COM_EV_APP_SHUTDOWN(self):
    
        caps = self.__get_capabilities()
        for notification_type, unique_service_name in caps:
            print notification_type, unique_service_name
            ssdp.broadcast_byebye(notification_type, unique_service_name)
        print "done shutdown"
                    
            
    def handle_HTTPSERVER_EV_REQUEST(self, owner, req):
    
        if (owner != self): return
        
        print "TCP REQUEST FROM", req.get_source()
        print " --", req.get_method(), req.get_path()
        
        method = req.get_method()
        path = req.get_path()
        
        if (method == "GET"):
            self.__handle_get(req)
        
        
        elif (method == "POST"):
            svc = self.__ctrl_urls.get(path)
            if (svc):
                print "SOAP REQUEST:", req.get_header("SOAPACTION")
                ok, response = svc.feed_soap(req.get_body())
                if (ok):
                    req.send_xml(response)
                else:
                    req.send_xml_error("500 Internal Server Error", response)
            else:
                req.send_not_found("MediaBox", path)
        
        
        elif (method == "SUBSCRIBE"):
            svc = self.__event_urls.get(path)
            callback = req.get_header("CALLBACK")
            nt = req.get_header("NT")
            sid = req.get_header("SID")
            timeout = req.get_header("TIMEOUT") or "Second-1800"
            timeout_val = int(timeout.upper().replace("SECOND-", ""))
        
            if (nt != "upnp:event" or 
                  (sid and nt or sid and callback) or
                  (not sid and not callback) or
                  not svc):
                req.send_code("HTTP/1.1 412 Precondition Failed")
            else:
                sid, actual_timeout = svc.subscribe(callback, sid, timeout_val)
                req.send("HTTP/1.1 200 OK",
                         {"SID": sid,
                          "TIMEOUT": "Second-%d" % actual_timeout},
                         "")
        
        
        elif (method == "UNSUBSCRIBE"):
            svc = self.__event_urls.get(path)
            callback = req.get_header("CALLBACK")
            nt = req.get_header("NT")
            sid = req.get_header("SID")
            
            if (not svc or not sid or callback or nt or
                not svc.unsubscribe(sid)):
                req.send_code("HTTP/1.1 412 Precondition Failed")
            else:
                req.send_ok()
        
        
        else:
            req.send_not_found("MediaBox", path)


    def handle_SSDP_EV_MSEARCH(self, req):
    
        self.__handle_msearch(req)

