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


class HTTPRequest(object):

    def __init__(self, method, path, protocol, headers, body, responder):
    
        print method, path, protocol
        self.__method = method
        self.__path = path
        self.__protocol = protocol
        self.__headers = headers
        self.__body = body
        self.__responder = responder
        
        
    def get_method(self):
    
        return self.__method
        
        
    def get_path(self):

        return network.URL(self.__path).path
        
                
    def get_query(self):

        return network.URL(self.__path).query
        
        
    def get_protocol(self):
    
        return self.__protocol
        
        
    def get_headers(self):
    
        return self.__headers.keys()
        
        
    def get_header(self, header):
    
        return self.__headers.get(header.upper(), "")
        
        
    def get_body(self):
    
        return self.__body
        
        
    def send(self, code, headers, body):
    
        self.__responder(code, headers, body)


    def send_ok(self):

        code = "HTTP/1.1 200 OK"
        headers = {}
        headers["CONNECTION"] = "close"
        
        self.__responder(code, headers, "")        


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

