from com import Component, msgs
from AVTransport import AVTransport
from ConnectionManager import ConnectionManager
from RenderingControl import RenderingControl
from upnp import ssdp
from utils import network
from utils import logging

import os
import commands


_SSDP_IP = "239.255.255.250"
_SSDP_PORT = 1900
_SERVICE_PORT = 47806

_UUID = "uuid:e09c6bee-7939-4fff-bf26-8d1f30ca6153"
_DEVICE_TYPE = "urn:schemas-upnp-org:device:MediaRenderer:2"

_CAPABILITIES = [
    ("upnp:rootdevice", _UUID + "::upnp:rootdevice"),
    (_UUID, _UUID),
    (_DEVICE_TYPE, _UUID + "::" + _DEVICE_TYPE),
              
    (AVTransport.SERVICE_TYPE, _UUID + "::" + AVTransport.SERVICE_TYPE),
    (ConnectionManager.SERVICE_TYPE, _UUID + "::" + ConnectionManager.SERVICE_TYPE),
    (RenderingControl.SERVICE_TYPE, _UUID + "::" + RenderingControl.SERVICE_TYPE)
]


_NOTIFY_ALIVE = """NOTIFY * HTTP/1.1
HOST:239.255.255.250:1900
CACHE-CONTROL: max-age = 1800
LOCATION: http://%s:%s/Description.xml
SERVER: Linux/2.6 UPnP/1.0 MediaBox/1.0
NT: %s
USN: %s
NTS:ssdp:alive\r\n\r\n"""


_BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class RootDevice(Component):
    """
    An embedded UPnP Media Renderer device.
    """

    def __init__(self):
    
        self.__av_transport = AVTransport(self)
        self.__connection_manager = ConnectionManager(self)
        self.__rendering_control = RenderingControl(self)
    
        Component.__init__(self)
        

    def __handle_ssdp(self, req):

        if (req.get_method() == "M-SEARCH" and
            req.get_header("MAN") == "\"ssdp:discover\""):
            host, port = req.get_source()
            mx = int(req.get_header("MX"))
        
            ip = network.get_ip()
            location = "http://%s:%s/Description.xml" % (ip, _SERVICE_PORT)
            requested_search_target = req.get_header("ST")

            logging.debug("[ssdp] responding to M-SEARCH")
            for search_target, unique_service_name in _CAPABILITIES:
                if (requested_search_target in ("ssdp:all", search_target)):
                    logging.debug("[ssdp] %s, %s", search_target, unique_service_name)     
                    max_age = ssdp.respond_to_msearch(host, port,
                                                      location, search_target,
                                                      unique_service_name)
                #end if
            #end for
        #end if


    def __handle_http(self, req):
    
        path = req.get_path()
        #print path

        if (req.get_method() == "GET"):
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
                
            #print req.get_path()
            #print req.get_headers()

        elif (req.get_method() == "SUBSCRIBE"):
            req.send_ok()


    def __serve_device_description(self, req):
        """
        Serves the UPnP device description.
        """
        
        ip = network.get_ip()
        url_base = "http://%s:%d/Description.xml" % (ip, _SERVICE_PORT)
        hostname = commands.getoutput("hostname")
        friendly_name = "MediaBox on %s" % hostname
        
        descr = open(os.path.join(_BASE_DIR, "Description.xml"), "r").read()
        descr = descr.replace("@@URL_BASE@@", url_base) \
                     .replace("@@FRIENDLY_NAME@@", friendly_name) \
                     .replace("@@UUID@@", _UUID) \
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
        for notification_type, unique_service_name in _CAPABILITIES:
            ssdp.broadcast_alive(location, notification_type,
                                 unique_service_name)


    def handle_COM_EV_APP_SHUTDOWN(self):
    
        for notification_type, unique_service_name in _CAPABILITIES:
            ssdp.broadcast_byebye(notification_type, unique_service_name)
        

                                     
            
    def handle_HTTPSERVER_EV_REQUEST(self, owner, req):
    
        if (owner != self): return
        print "REQUEST FROM", req.get_source()
            
        self.__handle_http(req)


    def handle_SSDP_EV_MSEARCH(self, req):
    
        self.__handle_ssdp(req)

