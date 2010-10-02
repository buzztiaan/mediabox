from com import UPnPService, msgs

import os


_SCPD_FILE = os.path.join(os.path.dirname(__file__), "AVTransport2.xml")


class AVTransport(UPnPService):

    def __init__(self, owner):
    
        UPnPService.__init__(self, owner,
                             "/ctrl/AVTransport",
                             "urn:schemas-upnp-org:service:AVTransport:2",
                             open(_SCPD_FILE).read())
                

    def SetAVTransportURI(self, InstanceID, CurrentURI, CurrentURIMetaData):
    
        
        self.emit_message(msgs.MEDIA_ACT_LOAD_URI, CurrentURI, "")
        
        return ()


    def Play(self, InstanceID, Speed):
    
        self.emit_message(msgs.MEDIA_ACT_PAUSE)
    
        
