"""
Asynchronous lowlevel HTTP connection.
"""

from HTTPResponse import HTTPResponse
from utils import threads
from utils import logging
from utils import maemo

import gobject
import socket
import urlparse


_BUFFER_SIZE = 4096
 
    
def parse_addr(addr):
    """
    Splits the given address URL into a tuple
    C{(host, port, path)}.
    
    @param addr: address URL
    @return: C{(host, port, path)}
    """
        
    urlparts = urlparse.urlparse(addr)
    
    netloc = urlparts.netloc.split(":")[0]
    path = urlparts.path
    if (urlparts.query):
        path += "?" + urlparts.query
    return (netloc, int(urlparts.port or 0), path)



_number_of_connections = 0
_connection_queue = []

_MAX_CONNECTIONS = 12


class HTTPConnection(object):
    """
    Class for making asynchronous HTTP connections.
    
    The user callback is invoked repeatedly as data comes in. Check for
    response.finished() to see if the transmission is complete.    
    """    
    
    def __init__(self, host, port = 80):

        self.__address = (host, port)
        self.__finished = False

        # ID for identifying this connection when debugging
        self.__id = hex(hash(self))[2:]

        self.__callback = None
        self.__user_args = []
        
        self.__data = ""
        self.__io_watch = None
        self.__timeout_handler = None
        self.__close_connection = True
        self.__sock = None
        self.__socket_connected = False
        
        self.__is_aborted = False

        if (not host in ("localhost", "127.0.0.1")):
            maemo.request_connection()



    def _get_id(self):
        """
        Returns the unique ID of this connection.
        
        @return: unique connection ID
        """
    
        return self.__id

        

    def redirect(self, host, port):
        """
        Redirects this HTTP connection to another host.
        
        @param host: host name
        @param port: port number
        """

        self.__address = (host, port)


    def __connect(self, host, port):

        def f(sock, host, port):
            try:
                # this somehow causes high CPU load when running threaded...
                # threading with PyGTK is really a mess
                logging.info("conn [%s]: connecting to %s:%d" \
                             % (self.__id, host, port or 80))
                sock.connect((host, port or 80))
            except:
                logging.error("conn [%s]: could not resolve hostname:\n%s" \
                              % (self.__id, logging.stacktrace()))
                threads.run_unthreaded(self.__abort,
                                       "Could not resolve hostname")
                return
            self.__socket_connected = True

        if (self.__sock):
            self.__sock.close()
            
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            import traceback; traceback.print_exc()
            return

        # connecting to a socket is blocking and thus should be run in a
        # thread
        self.__socket_connected = False
        threads.run_threaded(f, self.__sock, host, port)

        


    def wait_until_closed(self):
        """
        Waits until this connection gets closed.
        Returns C{False} in case of a connection timeout.
        """
        
        import gtk
        while (not self.__finished):
            if (gtk.events_pending()): gtk.main_iteration(False)
            
        return self.__is_aborted

        
    def putrequest(self, method, path, protocol = "HTTP/1.1"):
        """
        Puts a HTTP request. After issuing this command, use L{putheader}
        to set the HTTP headers and afterwards L{endheaders} to terminate the
        headers block.
        
        Example::
          request = HTTPConnection("localhost")
          request.putrequest("GET", "/index.html")
          request.putheader("Host", "localhost")
          request.endheaders()
          
        
        @param method: HTTP method, e.g. C{GET} or C{POST}
        @param path:   the requested path
        @param protocol: protocol version (optional, defaults to HTTP/1.1)
        """
    
        self.__data = "%s %s %s\r\n" % (method, path, protocol)
        
        if (protocol != "HTTP/1.1"):
            self.__close_connection = True
        
        
    def putheader(self, key, value):
        """
        Puts a HTTP header.
        
        @param key:   header name
        @param value: header value
        """
    
        self.__data += "%s: %s\r\n" % (key, value)
        
        
    def endheaders(self):
        """
        Terminates the headers block.
        """

        self.__data += "\r\n"
        
        
    def send(self, body, cb, *user_args):
        """
        Sends the HTTP request and installs the given callback handler for
        receiving the L{HTTPResponse}.
        
        Signature of the callback::
          def handler(response, *user_args)
        
        @param body: payload (may be an empty string)
        @param cb:   callback handler
        @param *user_args: variable list of user arguments to the callback handler
        """

        self.__callback = cb
        self.__user_args = user_args
        self.__data += body    

        try:
            self.__send(self.__data)
        except:
            import traceback; traceback.print_exc()


    def send_raw(self, raw, cb, *args):
        """
        Sends a raw request ignoring L{putrequest}, L{putheader}, and
        L{endheaders}.

        Signature of the callback::
          def handler(response, *user_args)
        
        @param raw: string containing the whole request including headers and payload
        @param cb:   callback handler
        @param *user_args: variable list of user arguments to the callback handler        
        """
    
        self.__callback = cb
        self.__user_args = args
        self.__data = raw

        self.__send(self.__data)


    def __send(self, data):
        global _number_of_connections, _connection_queue
        
        if (_number_of_connections >= _MAX_CONNECTIONS):
            _connection_queue.append((self.__send, data))
            logging.debug("conn [%s]: queueing for later" % self.__id)
            
        else:
            _number_of_connections += 1

            logging.debug("%d HTTP connections active" % _number_of_connections)
            self.__connect(*self.__address)
            self.__reset_timeout()
            self.__io_watch = gobject.io_add_watch(self.__sock, gobject.IO_OUT,
                                                   self.__on_send_request,
                                                   [self.__data])
        


    def __reset_timeout(self):
        """
        Resets the timeout handler to signalize that the connection is active.
        """
    
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
        self.__timeout_handler = gobject.timeout_add(10000, self.__on_timeout)
        
        
    def __on_timeout(self):
        """
        Reacts on connection timeout.
        """
    
        self.__abort("TIMEOUT")
        
        
        
    def cancel(self):
        """
        Aborts this connection. This is a no-op if the connection is already
        closed.
        """
        
        if (self.__sock):
            self.__abort("cancelled")
        
        
    def __on_send_request(self, sock, cond, data):

        self.__reset_timeout()
        if (not self.__socket_connected): return True
        
        http = data[0]
        length = sock.send(http)
        data[0] = http[length:]
        logging.debug("conn [%s]: sending HTTP request\n%s" % (self.__id, http))
        if (data[0]):
            return True

        else:
            logging.debug("conn [%s]: receiving HTTP response" % self.__id)
            self.__io_watch = gobject.io_add_watch(sock, gobject.IO_IN,
                                                   self.__on_receive_header,
                                                   [""])
            return False


    def __on_receive_header(self, sock, cond, data):

        self.__reset_timeout()
    
        data[0] += sock.recv(_BUFFER_SIZE)

        idx = data[0].find("\r\n\r\n")
        if (idx == -1):
            # the headers are not yet complete; read on
            return True
        
        header = data[0][:idx]
        body = data[0][idx + 4:]
        lines = header.splitlines()
        status_header = lines[0].upper()
        logging.debug("conn [%s]: received HTTP headers\n%s" % (self.__id, header))

        headers = {}
        for l in lines[1:]:
            idx = l.find(":")
            if (idx != -1):
                key = l[:idx].strip().upper()
                value = l[idx + 1:].strip()
                headers[key] = value
        #end for
        
        # check for connection keep-alive
        if (headers.get("CONNECTION", "").upper() == "KEEP-ALIVE"):
            logging.debug("conn [%s]: is keep-alive" % self.__id)
            self.__close_connection = False
            
        if (body):
            logging.debug("conn [%s]: receiving body" % self.__id)

        resp = HTTPResponse(status_header, headers)

        if (200 <= resp.get_status() < 210):
            # OK
            resp.feed(body)
            if (not resp.finished()):
                if (body): self.__callback(resp, *self.__user_args)
                self.__io_watch = gobject.io_add_watch(sock, gobject.IO_IN,
                                                       self.__on_receive_body,
                                                       resp)

            else:
                self.__callback(resp, *self.__user_args)
                self.__finish_download(resp)


        elif (300 <= resp.get_status() < 310):
            # redirect needed
            logging.debug("conn [%s]: HTTP redirect" % self.__id)
            self.__callback(resp, *self.__user_args)
            self.__check_connection_queue()

        elif (resp.get_status() == 404):
            # file not found; abort
            # TODO: invoke callback with error
            pass

        
        return False
        

    def __on_receive_body(self, sock, cond, resp):

        self.__reset_timeout()

        s = sock.recv(_BUFFER_SIZE)
        if (not s):
            # server closed connection
            resp.set_finished()

        logging.debug("conn [%s]: receiving body" % self.__id)
        resp.feed(s)

        if (not resp.finished()):
            # we're still waiting for data; read on
            self.__callback(resp, *self.__user_args)
            return True

        else:
            # finished downloading
            self.__callback(resp, *self.__user_args)
            self.__finish_download(resp)
            return False


    def __abort(self, error):
    
        self.__is_aborted = True
        self.__sock.close()
        self.__sock = None
        
        if (self.__io_watch):
            gobject.source_remove(self.__io_watch)
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)

        logging.error("conn [%s]: connection aborted (%s)" \
                      % (self.__id, error))
        self.__callback(None, *self.__user_args)
        self.__finished = True
        self.__check_connection_queue()


    def __finish_download(self, resp):

        if (self.__close_connection):
            self.__sock.close()
            self.__sock = None
            
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)

        logging.debug("conn [%s]: finished" % self.__id)
        self.__finished = True
        self.__check_connection_queue()


    def __check_connection_queue(self):
        global _number_of_connections, _connection_queue

        _number_of_connections -= 1
        logging.debug("%d HTTP connections in queue" % _number_of_connections)
        if (_connection_queue):
            f, data = _connection_queue.pop(0)
            f(data)



if (__name__ == "__main__"):
    import gtk
    import sys
    
    def f(resp):
        if (resp):
            print resp.read()

    host, port, path = parse_addr(sys.argv[1])
    conn = HTTPConnection(host, port)
    conn.putrequest("GET", path)
    conn.putheader("Host", port and "%s:%d" % (host, port) or host)
    conn.endheaders()
    conn.send("", f)

    gtk.main()

