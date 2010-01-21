"""
Lightweight HTTP file server.
"""


from utils import logging

import gobject
import gtk
import socket
import os
import time


# we could restrict the server to listen to localhost, but since there is
# access restriction and we might want to enable filesharing over UPnP, it's
# a good idea to bind to 0.0.0.0.
_HOST = "0.0.0.0"
_PORT = 5556


class _FileServer(object):
    """
    Singleton class for a simple asynchronous file server. It shuts down itself
    if not in use after a while.
    Access to files must be allowed explicitly using the 'allow' method.
    """
    
    def __init__(self):
    
        self.__files = {}
        self.__client_count = 0
        self.__timeout_handler = None
        self.__with_idle_timeout = True
        self.__sock = None
        

    def get_location(self):
    
        return "http://%s:%d" % ("127.0.0.1", _PORT)


    def set_timeout(self, value):
    
        self.__with_idle_timeout = value


    def allow(self, filepath, urlpath):
        """
        Allows access to the given file under the given urlpath.
        """
        
        self.__files[urlpath] = filepath
        self.__open_server_socket()


    def __open_server_socket(self):
    
        if (not self.__sock):
            self.__sock = socket.socket(socket.AF_INET)
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__sock.bind((_HOST, _PORT))
            self.__sock.listen(1)
    
            self.__server_handler = gobject.io_add_watch(self.__sock,
                                                         gobject.IO_IN,
                                                         self.__on_new_client)
            logging.info("FileServer activated on %s:%d" % (_HOST, _PORT))


    def __on_idle_timeout(self):
    
        if (self.__sock):
            gobject.source_remove(self.__server_handler)
            self.__sock.close()
            self.__sock = None

        self.__files.clear()
        self.__timeout_handler = None
        logging.info("FileServer disabled due to idle timeout")


    def __add_client(self):
    
        self.__client_count += 1
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
            self.__timeout_handler = None
    
    
    def __remove_client(self):
    
        self.__client_count -= 1
        if (self.__client_count == 0):
            if (self.__timeout_handler):
                gobject.source_remove(self.__timeout_handler)
            if (self.__with_idle_timeout):
                self.__timeout_handler = \
                              gobject.timeout_add(25000, self.__on_idle_timeout)
        
            


    def __on_new_client(self, sock, cond):
    
        cnx, addr = sock.accept()
        self.__add_client()
        gobject.io_add_watch(cnx, gobject.IO_IN | gobject.IO_HUP,           
                             self.__on_receive_request, [""])
        logging.debug("FileServer accepted new client")
        return True
        
        
    def __on_receive_request(self, sock, cond, data):
    
        data[0] += sock.recv(4096)
        
        idx = data[0].find("\r\n\r\n")
        if (idx == -1):
            # the headers are not yet complete; read on
            return True
            
        header = data[0][:idx]
        lines = header.splitlines()
        status_header = lines[0]
        logging.debug("FileServer received:\n%s" % data[0])

        headers = {}
        for l in lines[1:]:
            idx = l.find(":")
            if (idx != -1):
                key = l[:idx].strip().upper()
                value = l[idx + 1:].strip()
                headers[key] = value
        #end for

        if (status_header.upper().startswith("GET")):
            parts = status_header.split()
            path = parts[1]

            if (path in self.__files and os.path.exists(self.__files[path])):
                http = "HTTP/1.1 200 OK\r\n" \
                       "Content-Type: application/x-octet-stream\r\n" \
                       "Server: MediaBox Lightweight FileServer\r\n" \
                       "Connection: close\r\n" \
                       "Accept-Ranges: bytes\r\n" \
                       "\r\n"
                filepath = self.__files[path]
            
            else:
                http = "HTTP/1.0 404 NOT FOUND\r\n" \
                       "Server: MediaBox Lightweight FileServer\r\n" \
                       "Connection: close\r\n" \
                       "\r\n"
                filepath = None
        else:
            http = "HTTP/1.0 400 BAD REQUEST\r\n" \
                   "Server: MediaBox Lightweight FileServer\r\n" \
                   "Connection: close\r\n" \
                   "\r\n"
            filepath = None

        gobject.io_add_watch(sock, gobject.IO_OUT, self.__on_send_header,
                             filepath, [http])

        return False
        
        
        
    def __on_send_header(self, sock, cond, filepath, data):
      
        http = data[0]
        length = sock.send(http)
        data[0] = http[length:]
        logging.debug("FileServer sent:\n%s" % http)
        if (data[0]):
            return True

        else:
            if (not filepath):
                sock.close()
                self.__remove_client()
                return False
                
            try:
                partial = filepath + ".partial"
                fd = open(filepath, "r")
            except:
                import traceback; traceback.print_exc()
                sock.close()
                self.__remove_client()
                return False
        
            self.__io_watch = gobject.io_add_watch(sock,
                                               gobject.IO_OUT | gobject.IO_HUP,
                                                   self.__on_send_data,
                                                   fd, partial, [""], [False])
            return False



    def __on_send_data(self, sock, cond, fd, partial, data, eof):

        if (cond == gobject.IO_HUP):
            logging.debug("Client closed connection on FileServer")
            fd.close()
            sock.close()
            self.__remove_client()
            return False

        # this helps a bit against starvation of the gtk events due to too much
        # IO traffic
        if (gobject.main_depth() < 3): gtk.main_iteration(False)

        chunk = data[0]
        if (chunk):
            length = sock.send(chunk)
            #print length
            data[0] = chunk[length:]
                        
        else:
            if (eof[0]):
                sock.close()
                self.__remove_client()
                return False
        
            d = fd.read(4096)
            if (not d):
                # we reached the end of file
                if (not os.path.exists(partial)):
                    # file was transferred completely; close the connection
                    fd.close()
                    eof[0] = True
                else:
                    # file is still being transferred...
                    
                    # sleep a little because otherwise the IO callback is
                    # immediately called again resulting in high CPU load
                    # while we cannot send anything to the waiting client
                    time.sleep(0.05)
                    
                    #print "gotta wait"
                    return True
                
            #new_chunk = hex(len(d))[2:]
            #print new_chunk
            #new_chunk += "\r\n"
            new_chunk = d
            #new_chunk += "\r\n"
            data[0] = new_chunk
        
        return True


_singleton = _FileServer()
def FileServer(): return _singleton



if (__name__ == "__main__"):
    import gtk
    fs = FileServer()
    fs.set_timeout(False)
    fs.allow("/tmp/tube.flv", "/video.flv")
    gtk.main()

