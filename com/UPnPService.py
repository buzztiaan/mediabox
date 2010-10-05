from com import Component, msgs
from upnp.SOAPAdaptor import SOAPAdaptor
from io import HTTPConnection
from utils import network

import uuid
import time
import gobject


class UPnPService(Component, SOAPAdaptor):
    """
    Base class for UPnP services.
    """

    def __init__(self, ctrl_url, event_url, service_type, scpd_xml):
    
        self.__ctrl_url = ctrl_url
        self.__event_url = event_url
        
        # table: SID -> (callback, seq, expiration_time)
        self.__subscribers = {}
        
        # table: name -> value
        self.__state_variables = {}
        
        # list of changed variables
        self.__changed_variables = []
        
        Component.__init__(self)
        SOAPAdaptor.__init__(self,
                             service_type,
                             scpd_xml)


    def subscribe(self, callback, sid, timeout):
        """
        Subscribes a callback to this service, or renews the subscription.
        Returns the SID and the actual timeout in seconds.
        """

        # if we have no sid, it's a new subscription and we make up one
        if (not sid):
            sid = "uuid:" + str(uuid.uuid1())

        now = int(time.time())
        self.__subscribers[sid] = (callback, 0, now + 1800)
        gobject.timeout_add(500, self._welcome_new_subscriber)

        return (sid, 1800)


    def unsubscribe(self, sid):
        """
        Unsubscribes from this service. Returns C{True} if unsubscribing was
        successful, C{False} otherwise.
        """
        
        try:
            del self.__subscribers[sid]
        except:
            return False
            
        return True


    def _welcome_new_subscriber(self):
        """
        To be implemented by derived classes.
        """
    
        pass


    def __make_property_set(self, names):
    
        out = "<?xml version=\"1.0\"?>\n"
        out += "<e:propertyset xmlns:e=\"urn:schemas-upnp-org:event-1-0\">"
        
        for name in names:
            out += "<e:property>"
            out += "<%s>%s</%s>" % (name, self.__state_variables[name], name)
            out += "</e:property>"
        
        out += "</e:propertyset>"
        
        return out


    def _set_variable(self, name, value):
        """
        Changes or initially sets the value of a UPnP state variable.
        """
    
        if (not name in self.__state_variables):
            self.__state_variables[name] = ""
            
        old_value = self.__state_variables.get(name)
        if (old_value != value):
            self.__state_variables[name] = value
            self.__changed_variables.append(name)
            
            
    def _notify_subscribers(self):
        """
        Notifies all subscribers about the recently changed UPnP state variables.
        """
    
        now = time.time()
        for sid in self.__subscribers.keys():
            callback, seq, expiration_time = self.__subscribers[sid]

            # callback may consist of several URLs
            callbacks = callback.replace(" ", "") \
                                .replace("><", " ") \
                                .replace("<", "") \
                                .replace(">", "")

            # check for expiration
            now = time.time()
            if (now > expiration_time):
                del self.__subscribers[sid]
                continue
                        
            propset = self.__make_property_set(self.__changed_variables)

            for cb in callbacks.split():
                url = network.URL(cb)
                print url.host, url.port, cb
                conn = HTTPConnection(url.host, url.port)
                conn.putrequest("NOTIFY", url.path)
                conn.putheader("HOST", url.host + ":" + str(url.port))
                conn.putheader("CONTENT-TYPE", "text/xml")
                conn.putheader("CONTENT-LENGTH", len(propset))
                conn.putheader("NT", "upnp:event")
                conn.putheader("NTS", "upnp:propchange")
                conn.putheader("SID", sid)
                conn.putheader("SEQ", str(seq))
                conn.endheaders()
                conn.send(propset, lambda *a: True)
            #end for
            
            # increase sequence number
            if (seq < 0xffffffff):
                seq += 1
            else:
                seq = 1
            self.__subscribers[sid] = (callback, seq, expiration_time)
        #end for
            
        self.__changed_variables = []

