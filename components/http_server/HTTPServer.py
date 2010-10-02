from com import Component, msgs
from HTTPRequest import HTTPRequest
from utils import logging

from Queue import Queue
import threading
import socket
import gobject
import time


_METHODS_WITHOUT_PAYLOAD = ["GET", "NOTIFY", "M-SEARCH", "SUBSCRIBE"]
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
                             args = [owner, cnx])
        t.setDaemon(True)
        t.start()
        
        logging.info("HTTP server accepted new client")
        
        return True


    def __listen_for_dgram(self, addr, port, sock, owner):
    
        # table: src_addr -> data
        datas = {}
        
        while ((addr, port) in self.__listeners):
            data, src_addr = sock.recvfrom(1024)

            print "received datagram from %s" % str(src_addr)
            #print len(data), data


            if (not src_addr in datas):
                datas[src_addr] = ""

            if (data):
                datas[src_addr] += data
                
            processed = self.__process_data(datas[src_addr])
            if (processed):
                method, path, protocol, headers, body = processed            
                self.__emit_dgram(owner, sock, method, path, protocol, headers, body)
                del datas[src_addr]
            #end if
            
        #end while


    def __serve_client(self, owner, cnx):
        
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
                print "DATA", data
            except:
                receiving = False
            
            if (not data):
                receiving = False
            
            processed = self.__process_data(data)
            if (processed):
                method, path, protocol, headers, body = processed
                self.__emit(owner, cnx, method, path, protocol, headers, body)
                receiving = False
            #end if

        #end while


    def __process_data(self, data):
    
        if (not "\r\n\r\n" in data): return None
        
        complete = False
        
        idx = data.find("\r\n\r\n")
        hdata = data[:idx]
        body = data[idx + 4:]
        method, path, protocol, headers = self.__parse_headers(hdata)

        content_length = int(headers.get("CONTENT-LENGTH", "-1"))
        
        # abort if there's no payload to expect
        if (method in _METHODS_WITHOUT_PAYLOAD or 
            method.startswith("HTTP/") or content_length == 0):
            complete = True

        # check content length of body
        elif (content_length != -1 and len(body) >= content_length):
            complete = True

        if (complete):
            if (headers.get("TRANSFER-ENCODING", "").upper() == "CHUNKED"):
                body = self.__unchunk(body)
    
            return (method, path, protocol, headers, body)
        else:
            return None


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


    def __parse_headers(self, hdata):
    
        lines = hdata.splitlines()
        
        parts = [ p for p in lines[0].split() if p ]
        method = parts[0]
        try:
            path = parts[1]
        except:
            path = ""
        try:
            protocol = parts[2]
        except:
            protocol = "HTTP/1.0"

        headers = {}            
        for line in lines[1:]:
            idx = line.find(":")
            key = line[:idx].upper().strip()
            value = line[idx + 1:].strip()
            headers[key] = value
        #end for
        
        return (method, path, protocol, headers)



    def __unchunk(self, chunked_body):
    
        chunk_size = 0
        body = ""
        
        while (chunked_body):
            idx = chunked_body.find("\r\n", 1)
            if (idx != -1):
                chunk_size = int(chunked_body[:idx], 16)
                chunked_body = chunked_body[idx + 2:]
            else:
                # must not happen
                pass
                
            if (chunk_size == 0):
                # the final chunk is always of size 0
                break
            else:
                body += chunked_body[:chunk_size]
                chunked_body = chunked_body[chunk_size:]
        #end while

        return body    


    def __emit(self, owner, cnx, method, path, protocol, headers, body):
    
        def responder(code, headers, body):
            t = threading.Thread(target = self.__send_response,
                                 args = [cnx, code, headers, body])
            t.setDaemon(True)
            t.start()
    
        request = HTTPRequest(method, path, protocol, headers, body, responder)
        gobject.timeout_add(0, self.emit_message,
                            msgs.HTTPSERVER_EV_REQUEST,
                            owner, request)


    def __emit_dgram(self, owner, cnx, method, path, protocol, headers, body):
    
        def responder(code, headers, body):
            raise IOError("cannot send response data on UDP")
    
        request = HTTPRequest(method, path, protocol, headers, body, responder)
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
        
        t = threading.Thread(target = self.__listen_for_dgram, 
                             args = [addr, port, sock, owner])
        t.setDaemon(True)
        t.start()
                                       
        self.__listeners[(addr, port)] = _Listener(owner, sock, None)
        
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

