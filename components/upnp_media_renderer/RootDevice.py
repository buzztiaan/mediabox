from com import Component, msgs
from AVTransport import AVTransport
from ConnectionManager import ConnectionManager
from RenderingControl import RenderingControl
from upnp import ssdp
from utils import network
from utils import logging

import os
import commands



_SERVICE_PORT = 47806
_BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class RootDevice(Component):
    """
    An embedded UPnP Media Renderer device.
    """

    UUID = "uuid:e09c6bee-7939-4fff-bf26-8d1f30ca6153"
    DEVICE_TYPE = "urn:schemas-upnp-org:device:MediaRenderer:2"

    def __init__(self):
    
        # services provided by the device
        self.__services = []
        
        # table: ctrl_url -> service
        self.__ctrl_urls = {}
        
        # table: event_url -> service
        self.__event_urls = {}
    
        Component.__init__(self)
        
        self._add_service(AVTransport(),
                          "/ctrl/AVTransport", "/event/AVTransport")
        self._add_service(ConnectionManager(),
                          "/ctrl/ConnectionManager", "/event/ConnectionManager")
        self._add_service(RenderingControl(),
                          "/ctrl/RenderingControl", "/event/RenderingControl")
        
        
    def _add_service(self, service, ctrl_url, ev_url):
        """
        Adds a UPnP service to this device.
        """
    
        self.__services.append(service)
        self.__ctrl_urls[ctrl_url] = service
        self.__event_urls[ev_url] = service


    def __get_capabilities(self):
        """
        Builds a list of the device's capabilites as (ST, USN) tuples.
        """

        # build up capabilities
        caps = []
        caps.append(("upnp:rootdevice", self.UUID + "::upnp:rootdevice"))
        caps.append((self.UUID, self.UUID))
        caps.append((self.DEVICE_TYPE, self.UUID + "::" + self.DEVICE_TYPE))
        for svc in self.__services:
            caps.append((svc.SERVICE_TYPE, self.UUID + "::" + svc.SERVICE_TYPE))

        return caps


    def __handle_msearch(self, req):
        """
        Handles M-SEARCH discovery requests.
        """

        if (req.get_header("MAN") == "\"ssdp:discover\""):
            src_host, src_port = req.get_source()
            mx = int(req.get_header("MX"))
    
            ip = network.get_ip()
            location = "http://%s:%s/Description.xml" % (ip, _SERVICE_PORT)
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
            self.__serve_device_description(req)
            
        elif (path == "/RenderingControl2.xml"):
            filepath = os.path.join(_BASE_DIR, "RenderingControl2.xml")
            req.send_xml(open(filepath, "r").read())

        elif (path == "/ConnectionManager2.xml"):
            filepath = os.path.join(_BASE_DIR, "ConnectionManager2.xml")
            req.send_xml(open(filepath, "r").read())

        elif (path == "/AVTransport2.xml"):
            filepath = os.path.join(_BASE_DIR, "AVTransport2.xml")
            req.send_xml(open(filepath, "r").read())

        elif (path == "/icon.png"):
            iconpath = os.path.join(_BASE_DIR, "icon.png")
            req.send_file(open(iconpath, "r"), "icon.png", "image/png")
           
        else:
            req.send_not_found("MediaBox", path)

        return True


    def __serve_device_description(self, req):
        """
        Serves the UPnP device description.
        """
        
        ip = network.get_ip()
        url_base = "http://%s:%d" % (ip, _SERVICE_PORT)
        hostname = commands.getoutput("hostname")
        friendly_name = "MediaBox on %s" % hostname
        
        descr = open(os.path.join(_BASE_DIR, "Description.xml"), "r").read()
        descr = descr.replace("@@URL_BASE@@", url_base) \
                     .replace("@@DEVICE_TYPE@@", device_type) \
                     .replace("@@FRIENDLY_NAME@@", friendly_name) \
                     .replace("@@UUID@@", self.UUID) \
                     .replace("@@ICON_URL@@", "/icon.png") \
                     .replace("@@SCPD_URL_RENDERING_CONTROL@@", "/RenderingControl2.xml") \
                     .replace("@@SCPD_URL_CONNECTION_MANAGER@@", "/ConnectionManager2.xml") \
                     .replace("@@SCPD_URL_AV_TRANSPORT@@", "/AVTransport2.xml")
        
        req.send_xml(descr)
        
        
    def handle_COM_EV_APP_STARTED(self):

        ip = network.get_ip()
        error = self.call_service(msgs.HTTPSERVER_SVC_BIND,
                                  self, ip, _SERVICE_PORT)
        if (error):
            print "Error binding to TCP"

        location = "http://%s:%d/Description.xml" % (ip, _SERVICE_PORT)
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

