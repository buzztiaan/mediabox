"""
HTTP downloader.
"""

from utils import network
from utils import logging

from Queue import Queue
import threading
import httplib
import gtk
import gobject
import time


_CHUNK_SIZE = 65536


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
        
        while (not self.__is_finished):
            gtk.main_iteration(False)


    def __open(self, url):
            
        t = threading.Thread(target = self.__request_data, args = [url])
        t.setDaemon(True)
        t.start()
        

    def __request_data(self, url):
    
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
            import traceback; traceback.print_exc()
            print "on", self.__url
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
        try:
            self.__callback(data, amount, total, *self.__args)
        except:
            pass

        if (not data):
            self.__is_finished = True

