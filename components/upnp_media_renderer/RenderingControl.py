from upnp.UPnPService import UPnPService
from com import msgs

import os


_SCPD_FILE = os.path.join(os.path.dirname(__file__), "RenderingControl2.xml")


class RenderingControl(UPnPService):

    SERVICE_TYPE = "urn:schemas-upnp-org:service:RenderingControl:2"

    def __init__(self):
    
        UPnPService.__init__(self,
                             "urn:schemas-upnp-org:service:RenderingControl:2")

        self.set_prop(self.PROP_UPNP_SERVICE_TYPE,
                      "urn:schemas-upnp-org:service:RenderingControl:2")
        self.set_prop(self.PROP_UPNP_SERVICE_ID,
                      "RenderingControl")
                

    def get_scpd(self):
    
        return open(_SCPD_FILE, "r").read()        
        

    def GetVolume(self, Channel, InstanceID):
    
        print "GetVolume"
        print Channel, InstanceID
        
        return ("50",)


    def SetVolume(self, Channel, InstanceID, DesiredVolume):
    
        # not implemented
        #self.emit_message(msgs.MEDIA_ACT_SET_VOLUME, int(DesiredVolume))
        return ()
