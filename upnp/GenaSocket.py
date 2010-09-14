"""
Server socket for listening to GENA notifications.
"""

from io import HTTPConnection, parse_addr
from utils import logging
from utils.MiniXML import MiniXML

import socket
import commands
import fcntl
import struct
import gobject


_GENA_SUBSCRIBE = "SUBSCRIBE %s HTTP/1.1\r\n" \
                  "HOST: %s\r\n" \
                  "CALLBACK: <%s>\r\n" \
                  "NT: upnp:event\r\n" \
                  "TIMEOUT: Second-300\r\n" \
                  "\r\n"

_GENA_RENEW = "SUBSCRIBE: %s HTTP/1.1\r\n" \
              "HOST: %s\r\n" \
              "SID: %s\r\n" \
              "TIMEOUT: Second-300\r\n" \
              "\r\n"
                  
_GENA_UNSUBSCRIBE = "UNSUBSCRIBE %s HTTP/1.1\r\n" \
                    "HOST: %s\r\n" \
                    "SID: %s\r\n" \
                    "\r\n"

_GENA_RENEWAL = "RENEWAL: %s HTTP/1.1\r\n" \
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
    print "IFACE", iface
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
    @since: 0.96
    """

    def __init__(self):
    
        # table: SID -> [callbacks]
        self.__handlers = {}
        
        # table: SID -> [renewal handler]
        self.__renewal_handlers = {}
        
        # table: callback -> SID
        self.__cb_to_sid = {}
        
        # table: ev_url -> SID
        self.__url_to_sid = {}
        
        # table: SID -> ev_url
        self.__sid_to_url = {}
        
        
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
        """
        Spawns a new worker when a client connects.
        """
    
        cnx, addr = sock.accept()
        print "new GENA connection", addr
        
        event = EventHandler (cnx,
                          self.__process_event_body,
                          self.__finish_event_processing)
        
        return True


    def __process_event_body(self, event_instance, body, uuid):

        if (not uuid in self.__handlers):
            event_instance.send_answer("HTTP/1.1 412 Precondition Failed")
            return

        #print "BODY", body
        prop_set = MiniXML(body).get_dom()
        prop = prop_set.get_child()

        for change in prop.get_children():
            signal_name = "changed::" + change.get_name().lower()

            # notify all subscribers
            for cb in self.__handlers[uuid]:
                try:
                    signal_value = change.get_child().get_value()
                except:
                    import traceback; traceback.print_exc()
                    signal_value = ""

                try:
                    cb(signal_name, signal_value)
                except:
                    logging.error(logging.stacktrace())
            #end for

            print "signal emitted", signal_name, signal_value

        event_instance.send_answer("HTTP/1.1 200 OK")

        
    def __finish_event_processing (self, success):

        pass
            
            
    def __on_receive_confirmation(self, response, ev_url, cb = None):
        """
        Handles retrieval of subscription notifications."
        """
    
        if (response and response.finished()):
            if (response.get_status() == 200):
                #print response.get_status()
                #print response.get_headers()
                sid = response.get_header("SID")
                timeout = response.get_header("TIMEOUT")
                logging.debug("received GENA subscription confirmation:\n" \
                              "SID: %s\n" \
                              "Timeout: %s" % (sid, timeout))

                try:
                    timeout_seconds = int(timeout[len("Second-"):])
                except:
                    timeout_seconds = 300

                if (not sid in self.__handlers):
                    self.__handlers[sid] = []
    
                # initial subscription has a callback
                if (cb):
                    self.__handlers[sid].append(cb)
                    self.__cb_to_sid[cb] = sid
                    
                self.__url_to_sid[ev_url] = sid
                self.__sid_to_url[sid] = ev_url

                # schedule timely renewal
                if (not sid in self.__renewal_handlers):
                    timeout_msecs = max(60, timeout_seconds - 10) * 1000
                    renewal_handler = gobject.timeout_add(timeout_msecs,
                                                     self.__renew_subscription,
                                                     sid)
                    self.__renewal_handlers[sid] = renewal_handler
                
                
    def __renew_subscription(self, sid):
        """
        Timeout handler for renewing a subscription.
        """
    
        del self.__renewal_handlers[sid]
        ev_url = self.__sid_to_url[sid]

        print "RENEWING SUBSCRIPTION FOR", sid, ev_url
        host, port, path = parse_addr(ev_url)
        conn = HTTPConnection(host, port)
        conn.send_raw(_GENA_RENEW % (path, host, sid),
                      self.__on_receive_confirmation,
                      ev_url)
        
        
    def subscribe(self, ev_url, cb):
        """
        Subscribes the given callback to the given event URL.
        @since: 0.96
        """

        # create GENA socket when first used
        if (not self.__gena_socket):
            self.__gena_socket = self.__create_gena_socket()

        # only subscribe once per event URL
        if (ev_url in self.__url_to_sid):
            sid = self.__url_to_sid[ev_url]
            self.__handlers[sid].append(cb)
            
        print "SUBSCRIBING TO", ev_url
        host, port, path = parse_addr(ev_url)
        conn = HTTPConnection(host, port)
        conn.send_raw(_GENA_SUBSCRIBE % (path, host, self.__gena_url),
                      self.__on_receive_confirmation, ev_url, cb)


    def unsubscribe(self, cb):
        """
        Unsubscribes the given callback.
        @since: 0.96
        """

        if (cb in self.__cb_to_sid):
            sid = self.__cb_to_sid[cb]
            ev_url = self.__sid_to_url[sid]
            
            host, port, path = parse_addr(ev_url)
            conn = HTTPConnection(host, port)
            conn.send_raw(_GENA_UNSUBSCRIBE % (path, host, sid),
                          lambda a,b:True)

            self.__handlers[sid].remove(cb)
            if (not self.__handlers[sid]):                
                del self.__handlers[sid]
                del self.__sid_to_url[sid]
                del self.__url_to_sid[ev_url]

            del self.__renewal_handlers[sid]
            del self.__cb_to_sid[cb]
        #end if

        
_singleton = _GenaSocket()
def GenaSocket(): return _singleton


class EventHandler (object):
    """
    Class for handling incoming events (i.e. changes on the values of the
    server variables)
    """

    def __init__ (self, cnx, process_cb, finish_cb):
        """
        Creates a new GENA event handler.
        
        @param cnx: socket connection to peer
        @param process_cb: callback handler for processing the event data
        @param finish_cb: callback handler for finishing processing
        """

        self.__socket = cnx
        self.__process_cb = process_cb
        self.__finish_cb = finish_cb

        self.__io_handler = gobject.io_add_watch(cnx, gobject.IO_IN,
                                                 self.__on_event_io, [""])
        
        self.__timeout_handler = gobject.timeout_add(10000, self.__on_timeout)


    def __on_timeout(self):
        """
        Reacts on connection timeout.
        """

        self.__timeout_handler = None

        # close connection and finish with an error
        self.__socket.close()
        self.__working_callback_id = None
        gobject.idle_add(self.__do_finish, False)
        logging.error("GENA server connection timeout")


    def send_answer (self, response):

        self.__send_response(response, True)


    def __send_response(self, response, success):
        """
        Sends a HTTP response.
        """
    
        self.__io_handler = gobject.io_add_watch(self.__socket,
                                                 gobject.IO_OUT,
                                                 self.__on_response_io,
                                                 response, success)
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
        self.__timeout_handler = gobject.timeout_add(10000, self.__on_timeout)


    def __on_event_io(self, cnx, condition, data):
        """
        Handles retrieval of event data.
        """

        data[0] += cnx.recv(4096)

        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
            self.__timeout_handler = None

        # find end of header
        idx = data[0].find("\r\n\r\n")

        if (idx != -1):
            # header is complete
            header = data[0][:idx]
            body = data[0][idx + 4:]
            
            lines = header.splitlines()
            method = lines[0].upper()
            if (method.startswith("NOTIFY")):
                # read header values
                values = {}
                for line in lines[1:]:
                    idx = line.find(":")
                    if (idx != -1):
                        key = line[:idx].strip().upper()
                        value = line[idx + 1:].strip()
                        values[key] = value
                #end for
                
                if (not "NTS" in values):
                    # NTS is mandatory
                    self.__send_response("HTTP/1.1 400 Bad Request", False)
                    return False
                
                elif (values["NTS"] != "upnp:propchange") : 
                    # we only receive eventing messages
                    self.__send_response("HTTP/1.1 412 Precondition Failed",
                                         False)
                    return False
                
                if ("SID" in values) :
                    uuid = values["SID"]
                else:
                    # SID is mandatory
                    self.__send_response("HTTP/1.1 412 Precondition Failed",
                                         False)
                    return False

                if ("CONTENT-LENGTH" in values):
                    body_length = int(values["CONTENT-LENGTH"])
                else:
                    self.__send_response("HTTP/1.1 411 Length Required", False)
                    return False
                
                #TODO: check event key for missing eventing message

                # check if body is complete
                if (len(body) >= body_length):
                    self.__io_handler = None
                    self.__process_cb(self, body, uuid)
                    
                    if (not self.__io_handler):
                        # process callback handler hasn't set an action,
                        # which is a programming error
                        cnx.close()
                        raise NoAnswerSet
                    #end if
                    
                    return False
                    
                else:
                    self.__timeout_handler = \
                                  gobject.timeout_add(10000, self.__on_timeout)
                    return True
                #end if       

            else:
                # we only serve NOTIFY requests
                self.__send_response("HTTP/1.1 405 Method Not Allowed", False)
                return False

            #end if - startswith("NOTIFY")                                             
            
        else:
            # we haven't fully received the header yet and need more data
            self.__timeout_handler = \
                        gobject.timeout_add(10000, self.__on_timeout)
            return True
        #end if - header complete

        return False


    def __on_response_io(self, cnx, condition, response, success):
        """
        Handles sending of response data.
        """

        self.__io_handler = None
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
            self.__timeout_handler = None

        response += "\r\n\r\n"
        cnx.send(response)
        cnx.close()
        gobject.idle_add(self.__do_finish, success)

        return False


    def __do_finish(self, success):

        self.__finish_cb(success)



class NoAnswerSet (Exception):

    pass

