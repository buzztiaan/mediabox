from com import Component, msgs
from upnp.SOAPAdaptor import SOAPAdaptor


class UPnPService(Component, SOAPAdaptor):
    """
    Base class for UPnP services.
    """

    def __init__(self, owner, endpoint, service_type, scpd_xml):
    
        self.__owner = owner
        self.__endpoint = endpoint
        
        print "INITING SERVICE", endpoint
        Component.__init__(self)
        SOAPAdaptor.__init__(self,
                             service_type,
                             scpd_xml)
        print "OK"
        
        
    def handle_HTTPSERVER_EV_REQUEST(self, owner, request):
    
        if (owner != self.__owner): return
        
        if (request.get_path() == self.__endpoint):
            print "SERVICE REQUEST", owner, request.get_header("SOAPACTION")
            ok, response = self.feed_soap(request.get_body())
            if (ok):
                request.send_xml(response)
            else:
                request.send_xml_error("500 Internal Server Error", response)

