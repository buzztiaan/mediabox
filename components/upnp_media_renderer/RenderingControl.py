from com import UPnPService, msgs

import os


_SCPD_FILE = os.path.join(os.path.dirname(__file__), "RenderingControl2.xml")


class RenderingControl(UPnPService):

    def __init__(self, owner):
    
        UPnPService.__init__(self, owner,
                             "/ctrl/RenderingControl",
                             "urn:schemas-upnp-org:service:RenderingControl:2",
                             open(_SCPD_FILE).read())
        
        

    def GetVolume(self, Channel, InstanceID):
    
        print "GetVolume"
        print Channel, InstanceID
        
        return ("50",)

