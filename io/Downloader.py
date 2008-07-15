from HTTPConnection import HTTPConnection, parse_addr


class Downloader(HTTPConnection):
    """
    Class for handling asynchronous GET operations.
    """
    
    def __init__(self, url, cb, *args):
    
        host, port, path = parse_addr(url)
        HTTPConnection.__init__(self, host, port)
        self.putrequest("GET", path)
        self.putheader("Host", port and "%s:%d" % (host, port) or host)
        self.endheaders()
        self.send("", self.__on_receive_data, cb, args)



    def __on_receive_data(self, resp, cb, args):
    
        if (not resp): return
            
        status = resp.get_status()
        
        if (status == 200):
            amount, total = resp.get_amount()
            amount = min(amount, total)
            data = resp.read()
            if (data or resp.finished()):
                cb(data, amount, total, *args)

        elif (300 <= status < 310):
            location = resp.getheaders()["LOCATION"]
            host, port, path = parse_addr(location)
            self.redirect(host, port)
            self.putrequest("GET", path)
            self.putheader("Host", port and "%s:%d" % (host, port) or host)
            self.endheaders()
            self.send("", self.__on_receive_data, cb, args)
            
