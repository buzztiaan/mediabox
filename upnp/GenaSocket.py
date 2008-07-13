from utils.GAsyncHTTPConnection import GAsyncHTTPConnection, parse_addr
from utils import logging
from upnp.MiniXML import MiniXML

import socket
import commands
import fcntl
import struct
import gobject


# TODO: gupnp-network-light crashes when timeout is omitted and MediaBox
# causes high CPU load -> investigate!
_GENA_SUBSCRIBE = "SUBSCRIBE %s HTTP/1.1\r\n" \
                  "HOST: %s\r\n" \
                  "CALLBACK: <%s>\r\n" \
                  "NT: upnp:event\r\n" \
                  "TIMEOUT: Second-infinite\r\n" \
                  "\r\n"

_GENA_RENEW = "SUBSCRIBE: %s HTTP/1.1\r\n" \
              "HOST: %s\r\n" \
              "SID: %s\r\n" \
              "TIMEOUT: Second-infinite\r\n" \
              "\r\n"
                  
_GENA_UNSUBSCRIBE = "UNSUBSCRIBE %s HTTP/1.1\r\n" \
                    "HOST: %s\r\n" \
                    "SID: %s\r\n" \
                    "\r\n"                  



def _get_my_ip():
    """
    Returns the IP of this host on the network.
    """
    
    # find the network interface (look at the default gateway)
    iface = commands.getoutput("cat /proc/net/route" \
                               "|cut -f1,2" \
                               "|grep 00000000" \
                               "|cut -f1") \
            or "lo"

    # get the IP of the interface
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', iface[:15])
    )[20:24])


_PORT = 5555


class _GenaSocket(object):
    """
    Class for a GENA socket for subscribing/unsubscribing to GENA events
    and dispatching incoming events to registered callback handlers.
    """

    def __init__(self):
    
        # table: SID -> callback
        self.__handlers = {}
        
        # table: callback -> SID
        self.__sids = {}
        
        # table: SID -> ev_url
        self.__event_urls = {}
        
        
        # network location of this GENA socket
        self.__gena_url = ""

        # the socket for receiving GENA events; this is created only when
        # needed, i.e. once subscriptions are made
        self.__gena_socket = None
                
        
    def __create_gena_socket(self):
        """
        Creates an asynchronous socket for listening to GENA events.
        """
        
        self.__gena_url = "http://%s:%d" % (_get_my_ip(), _PORT)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", _PORT))
        sock.listen(1)
        
        gobject.io_add_watch(sock, gobject.IO_IN, self.__on_new_client)
        
        return sock
        
        
    def __on_new_client(self, sock, condition):
    
        cnx, addr = sock.accept()
        
        event = NewEvent ( cnx, self.__process_event_body, self.__finish_event_processing )
        
        return True


    def __process_event_body (self, event_instance, body, uuid):

        if not uuid in self.__handlers :
            event_instance.send_answer ( "HTTP/1.1 412 Precondition Failed" )
            return

        envelope = MiniXML(body).get_dom()
        resp = envelope.get_child()
            
        for entry in resp.get_children():
            signal_name = "changed::"
            signal_name += entry.get_name().lower()
            self.__handlers[uuid] ( signal_name, entry.get_child().get_value() )
            print 'signal emited', signal_name, entry.get_child().get_value()

        event_instance.send_answer ( "HTTP/1.1 200 OK" )

        
    def __finish_event_processing (self, success):

        pass
            
            
    def __on_receive_confirmation(self, success, response, ev_url, cb):
    
        if (success):
            if ( response.get_status().startswith ("HTTP/1.1 200 OK") ):
                print response.get_status()
                print response.get_headers()
                sid = response.get_header("SID")
                logging.debug("received SID: %s" % sid)
                self.__handlers[sid] = cb
                self.__sids[cb] = sid
                self.__event_urls[sid] = ev_url
        
                # TODO: schedule renewal
        
        
    def subscribe(self, ev_url, cb):
        """
        Subscribes the given callback to the given event URL.
        """

        # create GENA socket when first used
        if (not self.__gena_socket):
            self.__gena_socket = self.__create_gena_socket()

        host, port, path = parse_addr(ev_url)
        GAsyncHTTPConnection(host, port,
                             _GENA_SUBSCRIBE % (path, host, self.__gena_url),
                             self.__on_receive_confirmation, ev_url, cb)
        


    def unsubscribe(self, cb):
        """
        Unsubscribes the given callback.
        """

        if (cb in self.__sids):
            sid = self.__sids[cb]
            ev_url = self.__event_urls[sid]
            
            host, port, path = parse_addr(ev_url)
            GAsyncHTTPConnection(host, port,
                                _GENA_UNSUBSCRIBE % (path, host, sid),
                                lambda a,b:True)
            del self.__handlers[sid]
            del self.__sids[cb]
            del self.__event_urls[sid]
        #end if

        
_singleton = _GenaSocket()
def GenaSocket(): return _singleton


#Adding a header processing callback, this class can be extended to handle asyncronally any type of http incoming connection

class NewEvent (object):
    """
    Class to handle incoming http request that the servers sent to announce events (changes on the values of the variables)

    body_processing_callback, is called when the complete body has been recieved, so it can process it and sent the appropiate answer.
        It has three arguments (event_instance, body, uuid):
        - event_instance is this same instance, and is provided so the callback can send an answer to the server
        - body, is the body of the message
        - uuid, is the uuid of the subscription (NOT the uuid of the server)

    final_callback is called when there is an error (timeout f.e.) or when the answer to the server has been sent correctly.
        It has one argument (success)
        - success, True if everything went fine, False otherwise
    """

    def __init__ (self, socket, body_processing_callback, final_callback):

        self.__socket = socket
        self.__body_processing_callback = body_processing_callback
        self.__final_callback = final_callback

        data = ""
        self.__working_callback_id = gobject.io_add_watch(socket, gobject.IO_IN, self.__check_upnp_event, data)
        self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )


    def __del__(self):

        if ( self.__working_callback_id > 0 ):  gobject.source_remove (self.__timeout_callback_id)
        if ( self.__timeout_callback_id > 0 ):  gobject.source_remove (self.__working_callback_id)
        self.__socket.close()


    def __timeout (self):

        if ( self.__working_callback_id > 0 ):  gobject.source_remove (self.__timeout_callback_id)
        socket.close()
        self.__working_callback_id = 0
        self.__timeout_callback_id = 0
        gobject.idle_add ( self.__execute_final_callback, False )
        print 'DEBUG: Event http server timeout'
        return (False)


    def __check_upnp_event (self, socket, condition, data):

        data += socket.recv(4096)

        gobject.source_remove ( self.__timeout_callback_id )

        index = data.find ('\r\n\r\n')

        if ( index == -1 ) :  #the headers are not completely recieved yet, and so this callback needs to be called again when more data is available
            self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
            self.__working_callback_id = gobject.io_add_watch ( socket, gobject.IO_IN, self.__check_upnp_event, data )
            return (False)

        lines = data[:index+2].splitlines()
        method = lines[0].upper()
 
        if ( method.startswith("NOTIFY") ):

            values = {}
            for l in lines[1:]:
                idx = l.find(":")
                if not ( idx == -1 ):
                    key = l[:idx].strip().upper()
                    value = l[idx + 1:].strip()
                    values[key] = value
            #end for

            if (not "NTS" in values):
                self.__working_callback_id = gobject.io_add_watch(self.__socket, gobject.IO_OUT, self.__send_event_response, "HTTP/1.1 400 Bad Request", False)
                self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )
                return (False)

            elif (not values["NTS"] == "upnp:propchange") :  #this socket should only recieve eventing messages but just for checking
                self.__working_callback_id = gobject.io_add_watch(self.__socket, gobject.IO_OUT, self.__send_event_response, "HTTP/1.1 412 Precondition Failed", False)
                self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )
                return (False)

            if ( "SID" in values) :
                uuid = values["SID"]
            else:
                self.__working_callback_id = gobject.io_add_watch(self.__socket, gobject.IO_OUT, self.__send_event_response, "HTTP/1.1 412 Precondition Failed", False)
                self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )
                return (False)

            if ( "CONTENT-LENGTH" in values ) :
                body_length = int(values["CONTENT-LENGTH"])
            else :
                self.__working_callback_id = gobject.io_add_watch(self.__socket, gobject.IO_OUT, self.__send_event_response, "HTTP/1.1 411 Length Required", False)
                self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )
                return (False)

            #TODO check event key for missing eventing message

            if ( len(data[index+4:]) >= body_length ):
                self.__working_callback_id = 0  #just for precaution in case the body_processing_callback is not correctly set
                self.__timeout_callback_id = 0

                self.__body_processing_callback (self, data[index+4:], uuid)
                return (False)

            else :
                self.__working_callback_id = gobject.io_add_watch(socket, gobject.IO_IN, self.__get_more_data, data, uuid, body_length, index)
                self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )

            return (False)

        #endif

        #this socket can only handle notify requests.
        self.__working_callback_id = gobject.io_add_watch(self.__socket, gobject.IO_OUT, self.__send_event_response, "HTTP/1.1 405 Method Not Allowed", False)
        self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )
        return (False)

    def __get_more_data (self, socket, condition, data, uuid, body_length, index):

        data += socket.recv(4096)

        gobject.source_remove ( self.__timeout_callback_id )

        if ( len(data[index+4:]) >= body_length ):
            self.__working_callback_id = 0  #just for precaution in case the body_processing_callback is not correctly set
            self.__timeout_callback_id = 0

            self.__body_processing_callback (self, data[index+4:], uuid)
            return (False)

        self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )
        self.__working_callback_id = gobject.io_add_watch(socket, gobject.IO_IN, self.__get_more_data, data, uuid, body_length, index)   #still more part of the body to arrive
        return (False)

    
    def send_answer (self, response):

        self.__working_callback_id = gobject.io_add_watch(self.__socket, gobject.IO_OUT, self.__send_event_response, response, True)  #trigger the callback when the socket can be written without blocking
        self.__timeout_callback_id = gobject.timeout_add ( 10000, self.__timeout )


    def __send_event_response (self, socket, condition, response, success):

        response = response + "\r\n\r\n"
        socket.send (response)

        gobject.source_remove ( self.__timeout_callback_id )
        socket.close()
        self.__working_callback_id = 0
        self.__timeout_callback_id = 0
        gobject.idle_add ( self.__execute_final_callback, success )
        return (False)

    def __execute_final_callback (self, success):

        self.__final_callback (success)
        return (False)


