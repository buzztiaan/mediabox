from com import UPnPService, msgs

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

    SERVICE_TYPE = "urn:schemas-upnp-org:service:ConnectionManager:2"

    def __init__(self, owner):
    
        UPnPService.__init__(self, owner,
                             "/ctrl/ConnectionManager",
                             self.SERVICE_TYPE,
                             open(_SCPD_FILE).read())
                


    def GetProtocolInfo(self):
        
        return ("", _PROTOCOLS)

