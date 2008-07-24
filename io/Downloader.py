from HTTPConnection import HTTPConnection, parse_addr


class Downloader(HTTPConnection):
    """
    Class for handling asynchronous GET operations.
    
    The user callback is invoked repeatedly as data comes in.
    The transmission is finished when data = "" is passed to the callback.
    """
    
    def __init__(self, url, cb, *args):
    
        host, port, path = parse_addr(url)
        HTTPConnection.__init__(self, host, port)
        self.putrequest("GET", path, "HTTP/1.1")
        self.putheader("Host", port and "%s:%d" % (host, port) or host)
        self.putheader("User-Agent", "MediaBox")
        #self.putheader("Connection", "close")
        self.endheaders()
        self.send("", self.__on_receive_data, cb, args)



    def __on_receive_data(self, resp, cb, args):
    
        if (not resp): return
            
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
            location = resp.getheaders()["LOCATION"]
            host, port, path = parse_addr(location)
            self.redirect(host, port)
            self.putrequest("GET", path, "HTTP/1.1")
            self.putheader("Host", port and "%s:%d" % (host, port) or host)
            self.putheader("User-Agent", "MediaBox")
            #self.putheader("Connection", "close")
            self.endheaders()
            self.send("", self.__on_receive_data, cb, args)
            