"""
Asynchronous lowlevel HTTP connection.
"""

from HTTPResponse import HTTPResponse
from utils import logging

import gobject
import threading
import socket
import select


_BUFFER_SIZE = 65536
_CONNECTION_TIMEOUT = 10
_MAX_CONNECTIONS = 8

_connection_resource = threading.Semaphore(_MAX_CONNECTIONS)


class HTTPConnection(object):
    """
    Class for making asynchronous HTTP connections.
    
    The user callback is invoked repeatedly as data comes in. Check for
    response.finished() to see if the transmission is complete.    
    """    
    
    def __init__(self, host, port = 80):

        self.__address = (host, port)

        # event for signalizing that the connection has terminated
        self.__finished = threading.Event()

        # ID for identifying this connection when debugging
        self.__id = hex(hash(self))[2:]

        self.__callback = None
        self.__user_args = []
        
        self.__data = ""
        self.__close_connection = True
        self.__sock = None
        self.__socket_connected = False
        
        self.__is_aborted = False
        self.__redirect_handled = False


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

        if (self.__sock):
            self.__sock.close()
        self.__sock = None

        _connection_resource.release()

        self.__address = (host, port)
        self.__redirect_handled = True


    def __emit(self, cb, *args):
        
        def f(ready_ev, cb, *args):
            try:
                cb(*args)
            except:
                import traceback; traceback.print_exc()
                pass
            ready_ev.set()
        
        ready_ev = threading.Event()
        gobject.timeout_add(0, f, ready_ev, cb, *args)
        ready_ev.wait()


    def __connect(self, host, port):
        """
        Opens an asynchronous connection to the given host and port.
        Returns an event object that will signalize when the connection action
        terminated. Once this event is set, the connection status may be read.
        """

        logging.debug("[conn %s] new http connection: %s",
                      self._get_id(), "http://%s:%d" % (host, port))

        if (self.__sock):
            self.__sock.close()

        _connection_resource.acquire()
        self.__finished.clear()
            
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            import traceback; traceback.print_exc()
            return

        try:
            self.__sock.connect((host, port or 80))
        except:
            import traceback; traceback.print_exc()
            self.__emit(self.__abort, "Could not resolve hostname")
            return
            
        logging.debug("[conn %s] connected", self._get_id())
        self.__socket_connected = True


    def is_aborted(self):
        """
        Returns whether the connection has been aborted.
        """
    
        return self.__is_aborted
        

    def wait_until_closed(self):
        """
        Waits until this connection gets closed.
        Returns C{False} in case of a connection timeout.
        """

        logging.debug("[conn %s] waiting until closed", self._get_id())
        import gtk
        while (not self.__finished.is_set()):
            while (gtk.events_pending()):
                gtk.main_iteration(True)
        #end for
        logging.debug("[conn %s] finished waiting", self._get_id())

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
        
        
    def __io_thread(self, data):
        """
        Asynchronous thread for sending data.
        """

        self.__connect(*self.__address)

        if (not self.__socket_connected): return
        self.__redirect_handled = False

        # first send
        logging.debug("[conn %s] sending HTTP request", self._get_id())
        while (data and self.__sock):
            chunk = data[:_BUFFER_SIZE]
            data = data[_BUFFER_SIZE:]
            rfds, wfds, xfds = select.select([], [self.__sock], [],
                                             _CONNECTION_TIMEOUT)
            if (wfds):
                wfds[0].send(chunk)
            else:
                # timeout
                self.__emit(self.__abort, "TIMEOUT")
                return
        #end while

        # then receive
        logging.debug("[conn %s] receiving HTTP response", self._get_id())
        response = HTTPResponse()
        while (not response.finished() and self.__sock and
               not self.__redirect_handled):
            rfds, wfds, xfds = select.select([self.__sock], [], [],
                                             _CONNECTION_TIMEOUT)
            if (rfds):
                chunk = rfds[0].recv(_BUFFER_SIZE)
                if (len(chunk) == 0):
                    response.set_finished()
                    self.__emit(self.__abort, "CONNECTION RESET")
                    return
                else:
                    response.feed(chunk)
                    self.__emit(self.__callback, response, *self.__user_args)

            else:
                # timeout
                self.__emit(self.__abort, "TIMEOUT")
                return
        #end while
        
        
        # check for connection keep-alive
        if (response.get_header("CONNECTION").upper() == "KEEP-ALIVE"):
            logging.debug("[conn %s] is keep-alive", self._get_id())
            self.__close_connection = False
        
        self.__emit(self.__finish)
        
        
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

        t = threading.Thread(target = self.__io_thread,
                             args = [self.__data])
        t.setDaemon(True)
        t.start()
        

    def send_raw(self, raw, cb, *user_args):
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
        self.__user_args = user_args
        self.__data = raw

        t = threading.Thread(target = self.__io_thread,
                             args = [self.__data])
        t.setDaemon(True)
        t.start()
        
                
    def cancel(self):
        """
        Aborts this connection. This is a no-op if the connection is already
        closed.
        """
        
        logging.error("[conn %s] cancelled", self._get_id())
        if (self.__sock):
            self.__abort("cancelled")
        

    def __abort(self, error):
    
        self.__is_aborted = True
        if (self.__sock):
            self.__sock.close()
        self.__sock = None

        self.__finished.set()
        _connection_resource.release()

        logging.error("[conn %s] connection aborted (%s)",
                      self._get_id(), error)
        self.__callback(None, *self.__user_args)


    def __finish(self):

        if (self.__close_connection and self.__sock):
            self.__sock.close()
            self.__sock = None

        self.__finished.set()
        _connection_resource.release()
            
        logging.debug("[conn %s] connection finished", self._get_id())
        if (not self.__close_connection):
            logging.debug("[conn %s] connection still alive", self._get_id())
        


if (__name__ == "__main__"):
    from utils import network
    import gtk
    import sys
    
    gtk.gdk.threads_init()
    
    def f(resp):
        if (resp):
            print resp.read()
        if (resp.finished()):
            gtk.main_quit()

    addr = network.URL(sys.argv[1])
    
    conn = HTTPConnection(addr.host, addr.port)
    conn.putrequest("GET", addr.path)
    conn.putheader("Host", addr.port and "%s:%d" % (addr.host, addr.port) or addr.host)
    conn.endheaders()
    conn.send("", f)

    gtk.main()

