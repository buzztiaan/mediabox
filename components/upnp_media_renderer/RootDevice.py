from com import Component, msgs
from upnp.UPnPDevice import UPnPDevice
from AVTransport import AVTransport
from ConnectionManager import ConnectionManager
from RenderingControl import RenderingControl


class RootDevice(UPnPDevice):
    """
    An embedded UPnP Media Renderer device.
    """    

    def __init__(self):
    
        UPnPDevice.__init__(self,
                            AVTransport(),
                            ConnectionManager(),
                            RenderingControl())

        self.set_prop(self.PROP_UPNP_FRIENDLY_NAME,
                      "MediaBox Media Renderer")

        self.set_prop(self.PROP_UPNP_UDN,
                      "uuid:e09c6bee-7939-4fff-bf26-8d1f30ca6153")
        self.set_prop(self.PROP_UPNP_DEVICE_TYPE,
                      "urn:schemas-upnp-org:device:MediaRenderer:2")
        self.set_prop(self.PROP_UPNP_SERVICE_PORT,
                      47806)
