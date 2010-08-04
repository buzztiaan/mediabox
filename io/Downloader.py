"""
HTTP downloader.
"""

from utils import network
from utils import logging

from Queue import Queue
import threading
import httplib
import os
import gtk
import gobject
import time


_CHUNK_SIZE = 65536

_MAX_CONNECTIONS = 1


# every net connection puts a token into this queue and takes on from it when
# done
# while the queue is full, new connections have to wait for being able to
# put a token
# this way we limit the amount of concurrent connections
_connection_queue = Queue(_MAX_CONNECTIONS)


class Downloader(object):
    """
    Class for handling asynchronous GET operations.
    
    The user callback is invoked repeatedly as data comes in.
    The transmission is finished when data = "" is passed to the callback.
    The transmission aborted when data = None is passed to the callback.
    """
    
    def __init__(self, url, cb, *args):
    
        # queue of (data, amount, total) tuples
        self.__queue = Queue()
        
        self.__is_cancelled = False
        self.__is_finished = False
        
        self.__url = url
        self.__callback = cb
        self.__args = args
    
        # location history for avoiding redirect loops
        self.__location_history = []

        self.__open(url)


    def cancel(self):
    
        self.__is_cancelled = True


    def wait_until_closed(self):
        
        now = time.time()
        while (time.time() < now + 10 and not self.__is_finished):
            gtk.main_iteration(False)
        #end while
        if (self.__is_finished):
            print "closed"
        else:
            print "timeout"


    def __open(self, url):
            
        if (url.startswith("/")):
            # local file
            t = threading.Thread(target = self.__request_local, args = [url])
        else:
            # remote file
            t = threading.Thread(target = self.__request_data, args = [url])

        t.setDaemon(True)
        t.start()
        
        
    def __request_local(self, url):
    
        _connection_queue.put(True)
        
        try:
            total = os.stat(url).st_size
            fd = open(url, "r")
        except:
            self.__queue_response(None, 0, 0)
            return
            
        amount = 0
        while (True):
            data = fd.read(_CHUNK_SIZE)
            if (not data):
                break
            time.sleep(0.001)
            amount += len(data)
            self.__queue_response(data, amount, total)
        #end while
        
        try:
            fd.close()
        except:
            pass
        
        print "CLOSED", self.__url, amount, "read"
        self.__queue_response("", amount, total)


    def __request_data(self, url):
    
        _connection_queue.put(True)
    
        host, port, path = network.parse_addr(url)
        try:
            conn = httplib.HTTPConnection(host, port or 80)
            #print host, port, path
            conn.putrequest("GET", path)
            conn.putheader("User-Agent", "MediaBox")
            conn.putheader("Connection", "close")
            conn.endheaders()
            resp = conn.getresponse()
        except:
            self.__queue_response(None, 0, 0)
            return

        status = resp.status
        print self.__url, "STATUS", status, resp.reason
        
        if (status == 200):
            total = int(resp.getheader("Content-Length", "-1"))
            amount = 0
            
            while (not resp.isclosed()):
                data = ""
                while (len(data) < _CHUNK_SIZE):
                    d = resp.read(1024)
                    if (not d):
                        break
                    else:
                        data += d
                    time.sleep(0.001)
                #end while
                #data = resp.read(_CHUNK_SIZE)
                amount += len(data)
                if (data):
                    self.__queue_response(data, amount, total)
                
                if (not data or self.__is_cancelled):
                    resp.close()
                
            #end while
            print "CLOSED", self.__url, amount, "read"
            self.__queue_response("", amount, total)

        elif (300 <= status < 310):
            location = resp.getheader("Location")
            if (not location in self.__location_history):
                self.__location_history.append(location)
                logging.debug("HTTP redirect to %s" % location)
                gobject.timeout_add(0, self.__open, location)
            else:
                self.__location_history.append(location)
                logging.error("redirect loop detected:\n%s",
                              "\n-> ".join(self.__location_history))
                self.__queue_response(None, 0, 0)
    
        elif (400 <= status < 510):
            self.__queue_response(None, 0, 0)
            

    def __queue_response(self, data, amount, total):
    
        self.__queue.put((data, amount, total))
        gobject.idle_add(self.__send_response)
        
        
    def __send_response(self):
    
        data, amount, total = self.__queue.get_nowait()
        if (not data and not self.__is_finished):
            self.__is_finished = True
            _connection_queue.get()

        try:
            self.__callback(data, amount, total, *self.__args)
        except:
            pass

