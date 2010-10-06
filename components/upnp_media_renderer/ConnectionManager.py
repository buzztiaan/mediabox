from upnp.UPnPService import UPnPService
from com import msgs

import os


_SCPD_FILE = os.path.join(os.path.dirname(__file__), "ConnectionManager2.xml")

_PROTOCOLS = "http-get:*:audio/mpeg:*," \
             "http-get:*:application/ogg:*," \
             "http-get:*:audio/x-vorbis:*," \
             "http-get:*:audio/x-ms-wma:*," \
             "http-get:*:audio/x-ms-asf:*," \
             "http-get:*:audio/x-flac:*," \
             "http-get:*:audio/x-wav:*," \
             "http-get:*:audio/x-ac3:*," \
             "http-get:*:audio/x-m4a:*," \
             "http-get:*:video/x-theora:*," \
             "http-get:*:video/x-dirac:*," \
             "http-get:*:video/x-wmv:*," \
             "http-get:*:video/x-wma:*," \
             "http-get:*:video/x-msvideo:*," \
             "http-get:*:video/x-3ivx:*," \
             "http-get:*:video/x-matroska:*," \
             "http-get:*:video/mpeg:*," \
             "http-get:*:video/x-ms-asf:*," \
             "http-get:*:video/x-divx:*," \
             "http-get:*:video/x-ms-wmv:*"

class ConnectionManager(UPnPService):

    def __init__(self):
    
        UPnPService.__init__(self,
                             "urn:schemas-upnp-org:service:ConnectionManager:2")

        self.set_prop(self.PROP_UPNP_SERVICE_TYPE,
                      "urn:schemas-upnp-org:service:ConnectionManager:2")
        self.set_prop(self.PROP_UPNP_SERVICE_ID,
                      "ConnectionManager")
                

    def get_scpd(self):
    
        return open(_SCPD_FILE, "r").read()
        

    def GetProtocolInfo(self):
        
        return ("", _PROTOCOLS)

