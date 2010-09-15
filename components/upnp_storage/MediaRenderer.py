from com import MediaOutput, msgs
from io.FileServer import FileServer
from utils import urlquote
from theme import theme

import gobject
import time
from xml.etree import ElementTree
import os
import hashlib


_SERVICE_RENDERING_CONTROL_1 = "urn:schemas-upnp-org:service:RenderingControl:1"
_SERVICE_AV_TRANSPORT_1 = "urn:schemas-upnp-org:service:AVTransport:1"

_SERVICE_RENDERING_CONTROL_2 = "urn:schemas-upnp-org:service:RenderingControl:2"
_SERVICE_AV_TRANSPORT_2 = "urn:schemas-upnp-org:service:AVTransport:2"

_NS_AVT_1 = "urn:schemas-upnp-org:metadata-1-0/AVT_RCS"
_NS_AVT_2 = "urn:schemas-upnp-org:metadata-1-0/AVT/"


def _get_my_ip():
    """
    Returns the IP of this host on the network.
    """
    
    import commands
    import fcntl
    import socket
    import struct
    
    # find the network interface (look at the default gateway)
    iface = commands.getoutput("cat /proc/net/route" \
                               "|cut -f1,2" \
                               "|grep 00000000" \
                               "|cut -f1") \
            or "lo"

    # get the IP of the interface
    print "IFACE", iface
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', iface[:15])
    )[20:24])



def _parse_time(t):
    """
    Takes a time string of the form HH:MM:SS and returns the amount of seconds.
    Returns 0 if the input was invalid.
    """

    try:
        h, m, s = t.split(":")
        return int(h) * 3600 + \
               int(m) * 60 + \
               int(s)
    except:
        return 0
        

class MediaRenderer(MediaOutput):
    """
    Media output component for playing on a compatible UPnP MediaRenderer
    device.
    """

    # supported UPnP device types
    DEVICE_TYPES = ["urn:schemas-upnp-org:device:MediaRenderer:1",
                    "urn:schemas-upnp-org:device:MediaRenderer:2"]


    TITLE = "UPnP Device"
    

    def __init__(self, descr):

        self.__generation = 1
    
        self.__is_playing = False        
        self.__description = descr
        self.__ctx_id = 0

        self.__position = 0
        self.__total = 0

    
        MediaOutput.__init__(self)

        dtype = descr.get_device_type()
        if (dtype == "urn:schemas-upnp-org:device:MediaRenderer:1"):
            self.__generation = 1
            self.__av_transport = descr.get_service_proxy(_SERVICE_AV_TRANSPORT_1)
            self.__rendering_control = descr.get_service_proxy(_SERVICE_RENDERING_CONTROL_1)
            #print self.__media_renderer.__introspect__()        
            descr.subscribe(_SERVICE_AV_TRANSPORT_1, self.__on_signal)

        elif (dtype == "urn:schemas-upnp-org:device:MediaRenderer:2"):
            self.__generation = 2
            self.__av_transport = descr.get_service_proxy(_SERVICE_AV_TRANSPORT_2)
            self.__rendering_control = descr.get_service_proxy(_SERVICE_RENDERING_CONTROL_2)
            #print "INTRO", self.__av_transport.__introspect__()
            #print self.__media_renderer.__introspect__()        
            descr.subscribe(_SERVICE_AV_TRANSPORT_2, self.__on_signal)


        self.TITLE = descr.get_friendly_name()


    def __on_signal(self, sig, ev_xml):

        if (not ev_xml.strip()): return
        
        print "MEDIA EVENT:", ev_xml
        ev_tree = ElementTree.fromstring(ev_xml)
        inst_node = ev_tree[0]
        
        if (_NS_AVT_1 in ev_xml):
            ns_avt = _NS_AVT_1
        else:
            ns_avt = _NS_AVT_2
        
        transport_node = inst_node.find("{%s}TransportState" % ns_avt)
        duration_node = inst_node.find("{%s}CurrentMediaDuration" % ns_avt)
        if (duration_node == None):
            duration_node = inst_node.find("{%s}CurrentTrackDuration" % ns_avt)
        position_node = inst_node.find("{%s}RelativeTimePosition" % ns_avt)
        
        print transport_node, duration_node, position_node
        
        if (duration_node != None):
            self.__total = _parse_time(duration_node.get("val"))
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            self.__ctx_id, self.__position, self.__total)
                    
        if (position_node != None):
            self.__position = _parse_time(position_node.get("val"))
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            self.__ctx_id, self.__position, self.__total)
            
        if (transport_node != None):
            transport_state = transport_node.get("val")

            if (transport_state == "PLAYING"):
                self.__is_playing = True
                self.emit_event(self.EVENT_STATUS_CHANGED,
                                self.__ctx_id, self.STATUS_PLAYING)

            elif (transport_state == "PAUSED_PLAYBACK"):
                self.__is_playing = False
                self.emit_event(self.EVENT_STATUS_CHANGED,
                                self.__ctx_id, self.STATUS_STOPPED)
        
            elif (transport_state == "STOPPED"):
                self.__is_playing = False
                self.emit_event(self.EVENT_STATUS_CHANGED,
                                self.__ctx_id, self.STATUS_EOF)                
        #end if
        

    def load_audio(self, f):
    
        uri = f.get_resource()
        
        if (uri.startswith("/")):
            # local file needs to served on a webserver
            fs = FileServer()
            fs.set_timeout(False)
            ip = _get_my_ip()
            ext = os.path.splitext(uri)[1]
            path = "/" + hashlib.md5(uri).hexdigest() + ext
            url = "http://%s:5556%s" % (ip, path)
            fs.allow(uri, path)
        else:
            # remote file
            url = uri

        self.__position = 0
        self.__av_transport.SetAVTransportURI(None, "0", url, "")
        self.__av_transport.Play(None, "0", "1")
        
        self.__ctx_id = (time.time() * 1000)
        return self.__ctx_id


    def load_video(self, f):
    
        return self.load_audio(f)


    def play(self):
    
        self.__av_transport.Play(None, "0", "1")


    def pause(self):
    
        if (self.__is_playing):
            self.__av_transport.Pause(None, "0")
        else:
            self.__av_transport.Play(None, "0", "1")

        
    def stop(self):
    
        self.__av_transport.Pause(None, "0")


    def set_volume(self, vol):
    
        self.__rendering_control.SetVolume(None, "0", "Master", `vol`)

