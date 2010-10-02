from com import Component, msgs
from RenderingControl import RenderingControl
from AVTransport import AVTransport
from utils import network

import os
import commands


_SSDP_IP = "239.255.255.250"
_SSDP_PORT = 1900
_SERVICE_PORT = 47806

_UUID = "uuid:e09c6bee-7939-4fff-bf26-8d1f30ca6153"

_ADVERTISEMENT = """HTTP/1.1 200 OK
CACHE-CONTROL: max-age = 1800
EXT:
LOCATION: http://%s:%s/Description.xml
SERVER: Linux/2.6 UPnP/1.0 MediaBox/1.0
ST: "upnp:rootdevice"
USN: %s::upnp:rootdevice
\r\n\r\n"""

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class RootDevice(Component):
    """
    An embedded UPnP Media Renderer device.
    """

    def __init__(self):
    
        self.__rendering_control = RenderingControl((self, 1))
        self.__av_transport = AVTransport((self, 1))
    
        Component.__init__(self)
        
        
    def handle_COM_EV_APP_STARTED(self):
    
        error = self.call_service(msgs.HTTPSERVER_SVC_BIND_UDP,
                                  (self, 0), _SSDP_IP, _SSDP_PORT)
        if (error):
            print "Error binding to SSDP"

        ip = network.get_ip()
        error = self.call_service(msgs.HTTPSERVER_SVC_BIND,
                                  (self, 1), ip, _SERVICE_PORT)
        if (error):
            print "Error binding to TCP"


    def __handle_ssdp(self, req):
            
        if (req.get_method() == "M-SEARCH" and
            req.get_header("MAN") == "\"ssdp:discover\"" and
            req.get_header("ST") == "upnp:rootdevice"):
            host, port = req.get_header("HOST").split(":")
            mx = int(req.get_header("MX"))
        
            print "sending advertisement"
            ip = network.get_ip()
            network.send_datagram(host, int(port),
                                  _ADVERTISEMENT \
                                  % (ip, _SERVICE_PORT, _UUID))


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
                
            print req.get_path()
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
        
            
            
    def handle_HTTPSERVER_EV_REQUEST(self, owner, req):
    
        #print "REQUEST", req
        if (owner == (self, 0)):
            self.__handle_ssdp(req)
            
        elif (owner == (self, 1)):
            self.__handle_http(req)

