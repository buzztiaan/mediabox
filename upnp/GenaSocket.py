from utils.GAsyncHTTPConnection import GAsyncHTTPConnection, parse_addr
from utils import logging

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
        
        # lists are passed by reference, so we use a list to hold the data
        data = [""]
        gobject.io_add_watch(cnx, gobject.IO_IN, self.__on_receive_data, data)
        
        return True
        
        
    def __on_receive_data(self, cnx, condition, data):
    
        data[0] += cnx.recv(4096)
        
        # TODO: this check for EOF is bad; improve it
        if (data[0].strip()[-1] == ">"):
            print "closing socket"
            cnx.close()
            self.__process_event(data[0])
            return False
            
        else:
            return True


    def __process_event(self, data):
    
        print "received", data
            
            
    def __on_receive_confirmation(self, success, cnx, response, ev_url, cb):
    
        if (success):
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
                                lambda a,b,c:True)
            del self.__handlers[sid]
            del self.__sids[cb]
            del self.__event_urls[sid]
        #end if

        
_singleton = _GenaSocket()
def GenaSocket(): return _singleton

