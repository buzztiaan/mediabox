from com import MediaOutput, msgs
from io.FileServer import FileServer
from utils import urlquote
from theme import theme

import time


_SERVICE_RENDERING_CONTROL_1 = "urn:schemas-upnp-org:service:RenderingControl:1"
_SERVICE_AV_TRANSPORT_1 = "urn:schemas-upnp-org:service:AVTransport:1"

_SERVICE_RENDERING_CONTROL_2 = "urn:schemas-upnp-org:service:RenderingControl:2"
_SERVICE_AV_TRANSPORT_2 = "urn:schemas-upnp-org:service:AVTransport:2"



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
    
        self.__is_playing = False        
        self.__description = descr
        self.__ctx_id = 0

    
        MediaOutput.__init__(self)

        dtype = descr.get_device_type()
        if (dtype == "urn:schemas-upnp-org:device:MediaRenderer:1"):
            self.__av_transport = descr.get_service_proxy(_SERVICE_AV_TRANSPORT_1)
            self.__rendering_control = descr.get_service_proxy(_SERVICE_RENDERING_CONTROL_1)
            #print self.__media_renderer.__introspect__()        
            descr.subscribe(_SERVICE_AV_TRANSPORT_1, self.__on_signal)

        elif (dtype == "urn:schemas-upnp-org:device:MediaRenderer:2"):
            self.__av_transport = descr.get_service_proxy(_SERVICE_AV_TRANSPORT_2)
            self.__rendering_control = descr.get_service_proxy(_SERVICE_RENDERING_CONTROL_2)
            print "INTRO", self.__av_transport.__introspect__()
            #print self.__media_renderer.__introspect__()        
            descr.subscribe(_SERVICE_AV_TRANSPORT_2, self.__on_signal)


        self.TITLE = descr.get_friendly_name()


    def __on_signal(self, sig, ev_xml):
    
        if ("val=\"PLAYING\"" in ev_xml):
            self.__is_playing = True
            self.emit_event(self.EVENT_STATUS_CHANGED,
                            self.__ctx_id, self.STATUS_PLAYING)

        elif ("val=\"PAUSED_PLAYBACK\"" in ev_xml):
            self.__is_playing = False
            self.emit_event(self.EVENT_STATUS_CHANGED,
                            self.__ctx_id, self.STATUS_STOPPED)
        
        elif ("val=\"STOPPED\"" in ev_xml):
            self.__is_playing = False
            self.emit_event(self.EVENT_STATUS_CHANGED,
                            self.__ctx_id, self.STATUS_EOF)


    def load_audio(self, f):
    
        uri = f.get_resource()
        
        if (uri.startswith("/")):
            # local file needs to served on a webserver
            fs = FileServer()
            fs.set_timeout(False)
            ip = _get_my_ip()    
            url = "http://%s:5556%s" % (ip, urlquote.quote(uri))
            fs.allow(uri, urlquote.quote(uri))
        else:
            # remote file
            url = uri

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
    
        self.__av_transport.Stop(None, "0")


    def set_volume(self, vol):
    
        self.__rendering_control.SetVolume(None, "0", "Master", `vol`)

