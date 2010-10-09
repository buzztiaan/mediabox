"""
HTTP downloader.
"""


from HTTPConnection import HTTPConnection
from utils import network
from utils import logging

import gtk
import gobject
import threading
import os
import time


class Downloader(HTTPConnection):
    """
    Class for handling asynchronous GET operations.
    
    The user callback is invoked repeatedly as data comes in.
    The transmission is finished when data = "" is passed to the callback.
    """
    
    def __init__(self, url, cb, *args):
    
        # location history for avoiding redirect loops
        self.__location_history = []
    
        addr = network.URL(url)
        HTTPConnection.__init__(self, addr.host, addr.port)
        
        logging.debug("[downloader] retrieving: %s", url)
        
        if (url.startswith("/")):
            t = threading.Thread(target = self.__get_local_file,
                                 args = [url, cb, args])
            t.setDaemon(True)
            t.start()
            
        else:
            if (addr.query_string):
                path = addr.path + "?" + addr.query_string
            else:
                path = addr.path
            self.putrequest("GET", path, "HTTP/1.1")
            self.putheader("Host", "%s:%d" % (addr.host, addr.port))
            self.putheader("User-Agent", "MediaBox")
            #self.putheader("Connection", "close")
            self.endheaders()
            self.send("", self.__on_receive_data, cb, args)


    def __emit(self, cb, *args):

        def f(*args):
            ret = cb(*args)
            
        gobject.timeout_add(0, f, *args)


    def __get_local_file(self, url, cb, args):
        
        try:
            total = os.stat(url).st_size
            fd = open(url, "r")
        except:
            self.__emit(cb, None, 0, 0, *args)
            return
            
        amount = 0
        while (True):
            data = fd.read(65536)
            if (not data):
                break
            time.sleep(0.001)
            amount += len(data)
            self.__emit(cb, data, amount, total, *args)
        #end while
        
        try:
            fd.close()
        except:
            pass
        
        self.__emit(cb, "", amount, total, *args)


    def __on_receive_data(self, resp, cb, args):
    
        if (not resp):
            cb(None, 0, 0, *args)
            return
            
        status = resp.get_status()
        
        if (status == 200):
            amount, total = resp.get_amount()
            data = resp.read()
            if (data):
                #print data
                cb(data, amount, total, *args)
            
            if (not data or resp.finished()):
                cb("", amount, total, *args)

        elif (300 <= status < 310):
            location = resp.get_header("LOCATION")
            if (not location in self.__location_history):
                self.__location_history.append(location)
                addr = network.URL(location)
                logging.debug("HTTP redirect to %s" % location)
                self.redirect(addr.host, addr.port)
                if (addr.query_string):
                    path = addr.path + "?" + addr.query_string
                else:
                    path = addr.path
                self.putrequest("GET", path, "HTTP/1.1")
                self.putheader("Host", "%s:%d" % (addr.host, addr.port))
                self.putheader("User-Agent", "MediaBox")
                #self.putheader("Connection", "close")
                self.endheaders()
                self.send("", self.__on_receive_data, cb, args)
            else:
                self.__location_history.append(location)
                logging.error("[downloader] redirect loop detected:\n%s",
                              "\n-> ".join(self.__location_history))
                cb(None, 0, 0, *args)
                return
    
        elif (400 <= status < 510):
            cb(None, 0, 0, *args)
            return

        # try to avoid starvation of GTK for high bandwidths
        #then = time.time() + 0.1
        #while (gtk.events_pending() and time.time() < then):
        #    gtk.main_iteration(False)

