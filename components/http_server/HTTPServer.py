from com import Component, msgs
from HTTPRequest import HTTPRequest
from utils import logging
from utils import network

from Queue import Queue
import threading
import socket
import gobject
import time


_SERVER_AGENT = "Embedded HTTP Server/1.0.1"


class _Listener(object):
    def __init__(self, owner, sock, iowatch):
        self.owner = owner
        self.sock = sock
        self.iowatch = iowatch



class HTTPServer(Component):
    """
    Embedded HTTP server component.
    """

    def __init__(self):
    
        # table: (addr, port) -> listener
        self.__listeners = {}
    
        Component.__init__(self)


    def __on_new_client(self, sock, cond, owner):
    
        cnx, addr = sock.accept()
        
        t = threading.Thread(target = self.__serve_client, 
                             args = [owner, cnx, addr])
        t.setDaemon(True)
        t.start()
        
        logging.info("HTTP server accepted new client")
        
        return True


    def __listen_for_dgram(self, addr, port, sock, owner):
    
        # table: src_addr -> data
        datas = {}
        
        while ((addr, port) in self.__listeners):
            print "listening for datagram"
            data, src_addr = sock.recvfrom(1024)

            print "received datagram from %s" % str(src_addr)
            #print len(data), data


            if (not src_addr in datas):
                datas[src_addr] = ""

            if (data):
                datas[src_addr] += data
                
            processed = network.parse_http(datas[src_addr])
            if (processed):
                method, path, protocol, headers, body = processed            
                self.__emit_dgram(owner, sock, src_addr, method, path, protocol,
                                  headers, body)
                del datas[src_addr]
            #end if
            
        #end while


    def __serve_client(self, owner, cnx, src_addr):
        
        data = ""
        #method = ""
        #path = ""
        #protocol = ""
        #headers = {}
        #body = ""
        
        content_length = -1
        
        receiving = True
        while (receiving):
            try:
                data += cnx.recv(4096)
                #print "DATA", data
            except:
                receiving = False
            
            if (not data):
                receiving = False
            
            processed = network.parse_http(data)
            if (processed):
                method, path, protocol, headers, body = processed
                self.__emit(owner, cnx, src_addr, method, path, protocol,
                            headers, body)
                receiving = False
            #end if

        #end while


    def __send_response(self, cnx, code, headers, body):
    
        if (not "SERVER" in headers):
            headers["SERVER"] = _SERVER_AGENT
    
        is_fd = hasattr(body, "read")
        if (is_fd):
            headers["TRANSFER-ENCODING"] = "chunked"
            
        # send header
        data = code + "\r\n"
        data += "\r\n".join([ key + ": " + value
                              for key, value in headers.items() ])
        data += "\r\n\r\n"
        cnx.send(data)
        
        t = time.time()

        # send payload
        if (is_fd):
            while (True):
                try:
                    chunk = body.read(4096)
                except:
                    chunk = ""
                size = hex(len(chunk))[2:]
                try:
                    cnx.send(size + "\r\n")
                    if (chunk): cnx.send(chunk)
                except:
                    break
                
                if (len(chunk) == 0):
                    break
            #end while

        else:
            cnx.send(body)

        cnx.close()
        logging.info("sent - %s - [%ds]", code, int(time.time() - t))


    def __emit(self, owner, cnx, src_addr, method, path, protocol, headers, body):
    
        def responder(code, headers, body):
            print "RESPONDING", code
            t = threading.Thread(target = self.__send_response,
                                 args = [cnx, code, headers, body])
            t.setDaemon(True)
            t.start()
    
        request = HTTPRequest(method, path, protocol, headers, body, responder)
        request.set_source(src_addr)
        gobject.timeout_add(0, self.emit_message,
                            msgs.HTTPSERVER_EV_REQUEST,
                            owner, request)


    def __emit_dgram(self, owner, cnx, src_addr, method, path, protocol, headers, body):
    
        def responder(code, headers, body):
            raise IOError("cannot send response data on UDP")
    
        request = HTTPRequest(method, path, protocol, headers, body, responder)
        request.set_source(src_addr)
        gobject.timeout_add(0, self.emit_message,
                            msgs.HTTPSERVER_EV_REQUEST,
                            owner, request)


    def handle_HTTPSERVER_SVC_BIND(self, owner, addr, port):
    
        if ((addr, port) in self.__listeners):
            return "address already in use"
            
        try:
            sock = socket.socket(socket.AF_INET)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((addr, port))
            sock.listen(1)
        except:
            logging.error("error binding HTTP server to %s:%d\n%s", addr, port,
                          logging.stacktrace())
            return "could not bind to address"
        
        iowatch = gobject.io_add_watch(sock, gobject.IO_IN,
                                       self.__on_new_client,
                                       owner)
                                       
        self.__listeners[(addr, port)] = _Listener(owner, sock, iowatch)
        
        logging.info("bound HTTP server to TCP %s:%d", addr, port)
        
        return ""


    def handle_HTTPSERVER_SVC_BIND_UDP(self, owner, addr, port):
    
        if ((addr, port) in self.__listeners):
            return "address already in use"
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                 socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((addr, port))
        except:
            logging.error("error binding HTTP server to %s:%d\n%s", addr, port,
                          logging.stacktrace())
            return "could not bind to address"
        
        self.__listeners[(addr, port)] = _Listener(owner, sock, None)

        t = threading.Thread(target = self.__listen_for_dgram, 
                             args = [addr, port, sock, owner])
        t.setDaemon(True)
        t.start()
                                       
        
        logging.info("bound HTTP server to UDP %s:%d", addr, port)
        
        return ""
      
        
    def handle_HTTPSERVER_SVC_UNBIND(self, owner, addr, port):
    
        listener = self.__listeners.get((addr, port))
        if (listener and owner == listener.owner):
            if (listener.iowatch):
                gobject.source_remove(listener.iowatch)
            listener.sock.close()
            del self.__listeners[(addr, port)]

            logging.info("unbound HTTP server from %s:%d", addr, port)
            
        else:
            logging.warning("cannot unbind HTTP server from %s:%d", addr, port)
        
        #end if
    
        return ""

