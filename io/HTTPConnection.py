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
_CONNECTION_TIMEOUT = 30

_connection_resource = threading.Semaphore(4)


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
        """
        Opens an asynchronous connection to the given host and port.
        Returns an event object that will signalize when the connection action
        terminated. Once this event is set, the connection status may be read.
        """

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
            gobject.timeout_add(0, self.__abort, "Could not resolve hostname")
            return
            
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

        self.__finished.wait()        
            
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
        
        
    def __send_thread(self, data):
        """
        Asynchronous thread for sending data.
        """

        self.__connect(*self.__address)

        if (not self.__socket_connected): return

        # first send
        while (data):
            chunk = data[:4096]
            data = data[4096:]
            rfds, wfds, xfds = select.select([], [self.__sock], [],
                                             _CONNECTION_TIMEOUT)
            if (wfds):
                wfds[0].send(chunk)
            else:
                # timeout
                gobject.timeout_add(0, self.__abort, "TIMEOUT")
                return
        #end while

        # then receive
        response = HTTPResponse()
        while (not response.finished()):
            rfds, wfds, xfds = select.select([self.__sock], [], [],
                                             _CONNECTION_TIMEOUT)
            if (rfds):
                chunk = rfds[0].recv(4096)
                response.feed(chunk)
                gobject.timeout_add(0, self.__callback,
                                    response, *self.__user_args)

            else:
                # timeout
                gobject.timeout_add(0, self.__abort, "TIMEOUT")
                return
        #end while
        
        # check for connection keep-alive
        if (response.get_header("CONNECTION").upper() == "KEEP-ALIVE"):
            logging.debug("conn [%s]: is keep-alive" % self.__id)
            self.__close_connection = False
        
        gobject.timeout_add(0, self.__finish)
        
        
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

        t = threading.Thread(target = self.__send_thread,
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

        t = threading.Thread(target = self.__send_thread,
                             args = [self.__data])
        t.setDaemon(True)
        t.start()
        
                
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

        else:
            self.__callback(resp, *self.__user_args)

        
        return False
        

    def __abort(self, error):
    
        self.__is_aborted = True
        if (self.__sock):
            self.__sock.close()
        self.__sock = None

        self.__finished.set()
        _connection_resource.release()

        logging.error("conn [%s]: connection aborted (%s)" \
                      % (self.__id, error))
        self.__callback(None, *self.__user_args)


    def __finish(self):

        if (self.__close_connection and self.__sock):
            self.__sock.close()
            self.__sock = None

        self.__finished.set()
        _connection_resource.release()
            
        logging.debug("conn [%s]: finished" % self.__id)
        


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

