from HTTPResponse import HTTPResponse
from utils import network


_NOT_FOUND = """
<html>
<head><title>%s</title></head>
<body>
<p>Oops, the file you're looking for isn't there...</p>
<p>Not found: %s</p>
<hr>
<address>MediaBox Embedded HTTP Server</address>
</body>
</html>
"""


_STATE_NEW = 0
_STATE_HEADERS_DONE = 1
_STATE_BODY_DONE = 2


class HTTPRequest(HTTPResponse):

    def __init__(self):

        HTTPResponse.__init__(self)

        self.__source_address = ("127.0.0.1", 0)
        self.__responder = None
        
        
    def set_responder(self, responder):
        """
        Sets a responder function for sending a response.
        
        Signature: void responder(int code, dict headers, string body)
        """
    
        self.__responder = responder
        
        
    def set_source(self, src_addr):
    
        self.__source_address = src_addr
        
        
    def get_source(self):
    
        return self.__source_address
        
        
    def get_method(self):
    
        return self._get_headers().method
        
        
    def get_path(self):

        return network.URL(self._get_headers().path).path
        
                
    def get_query(self):

        return network.URL(self._get_headers().path).query
        
        
    def get_protocol(self):
    
        return self._get_headers().protocol
        
        
    def send(self, code, headers, body):
    
        self.__responder(code, headers, body)


    def send_code(self, code):

        headers = {}
        headers["CONNECTION"] = "close"
    
        self.__responder(code, headers, "")


    def send_ok(self):

        self.send_code("HTTP/1.1 200 OK")


    def send_html(self, html, charset = "utf-8"):
    
        code = "HTTP/1.1 200 OK"
        headers = {}
        headers["CONTENT-LENGTH"] = str(len(html))
        headers["CONTENT-TYPE"] = "text/html; charset=%s" % charset
        headers["CONNECTION"] = "close"
        
        self.__responder(code, headers, html)


    def send_xml(self, xml, charset = "utf-8"):
    
        code = "HTTP/1.1 200 OK"
        headers = {}
        headers["CONTENT-LENGTH"] = str(len(xml))
        headers["CONTENT-TYPE"] = "text/xml; charset=%s" % charset
        headers["CONNECTION"] = "close"
        
        self.__responder(code, headers, xml)


    def send_file(self, fd, name, mimetype):
    
        code = "HTTP/1.1 200 OK"
        
        headers = {}
        headers["CONTENT-TYPE"] = mimetype
        headers["CONNECTION"] = "close"
        headers["ACCEPT-RANGES"] = "bytes"
        headers["CONTENT-DISPOSITION"] = "inline; filename=\"%s\"" % name
        
        self.__responder(code, headers, fd)


    def send_error(self, code, html, charset = "utf-8"):
    
        headers = {}
        headers["CONTENT-LENGTH"] = str(len(html))
        headers["CONTENT-TYPE"] = "text/html; charset=%s" % charset
        headers["CONNECTION"] = "close"
        
        self.__responder("HTTP/1.1 " + code, headers, html)


    def send_xml_error(self, code, xml, charset = "utf-8"):
    
        headers = {}
        headers["CONTENT-LENGTH"] = str(len(xml))
        headers["CONTENT-TYPE"] = "text/xml; charset=%s" % charset
        headers["CONNECTION"] = "close"
        
        self.__responder("HTTP/1.1 " + code, headers, xml)

    
    def send_redirect(self, location):
    
        self.__responder("HTTP/1.1 302 Redirect",
                         {"LOCATION": location},
                         "<html><body>" \
                         "  Resource moved: <a href='%s'>%s</a>"\
                         "</body></html>" \
                         % (location, location))


    def send_not_found(self, title, location):
    
        self.send_error("404 Not Found", _NOT_FOUND % (title, location))

