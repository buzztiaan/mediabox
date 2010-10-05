from com import UPnPService, msgs

import os


_SCPD_FILE = os.path.join(os.path.dirname(__file__), "AVTransport2.xml")


class AVTransport(UPnPService):

    SERVICE_TYPE = "urn:schemas-upnp-org:service:AVTransport:2"

    def __init__(self):
    
        self.__next_uri = ""
    
        UPnPService.__init__(self,
                             "/ctrl/AVTransport",
                             "/event/AVTransport",
                             self.SERVICE_TYPE,
                             open(_SCPD_FILE).read())


    def _welcome_new_subscriber(self):
    
        self._set_variable("LastChange", "")
        self._notify_subscribers()


    def SetAVTransportURI(self, InstanceID, CurrentURI, CurrentURIMetaData):
        
        self.emit_message(msgs.MEDIA_ACT_LOAD_URI, CurrentURI, "")
        
        return ()


    def SetNextAVTransportURI(self, InstanceID, NextURI, NextURIMetaData):
        
        self.__next_uri = ""
        
        return ()


    def Play(self, InstanceID, Speed):
    
        self.emit_message(msgs.MEDIA_ACT_PLAY)
    

    def Pause(self, InstanceID):
    
        self.emit_message(msgs.MEDIA_ACT_PAUSE)


    def Stop(self, InstanceID):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)


    def Previous(self, InstanceID):
    
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def Next(self, InstanceID):
    
        self.emit_message(msgs.MEDIA_ACT_NEXT)


    def Seek(self, InstanceID, Unit, Target):
    
        self.emit_message(msgs.MEDIA_ACT_SEEK, int(Target))


    def handle_MEDIA_EV_EOF(self):
    
        if (self.__next_uri):
            self.emit_message(msgs.MEDIA_ACT_LOAD_URI, self.__next_uri, "")
            self.__next_uri = ""
            
