import urlparse
import commands
import fcntl
import socket
import struct
import threading


_METHODS_WITHOUT_PAYLOAD = ["GET", "NOTIFY", "M-SEARCH", "SUBSCRIBE"]


class URL(object):
    """
    Convenient class for working with URLs.
    @since: 2010.09.21
    """

    def __init__(self, url):
    
        self.scheme = ""
        self.netloc = ""
        self.host = ""
        self.port = ""
        self.path = ""
        self.query = {}
        self.query_string = ""
        
        parts = urlparse.urlparse(url)
        self.scheme = parts.scheme
        self.host = parts.netloc.split(":")[0]
        self.port = parts.port or 80
        self.netloc = parts.netloc
        self.path = parts.path
        self.query_string = parts.query
        self.__parts = parts
        
        try:
            # python 2.6 or later
            self.query = urlparse.parse_qs(parts.query)
        except:
            # python 2.5
            import cgi
            self.query = cgi.parse_qs(parts.query)
        
        
    def __str__(self):
    
        return self.__parts.geturl()


def get_ip():
    """
    Returns the IP address of the default interface.
    
    @todo: IPv6
    """

    # find the network interface (look at the default gateway)
    iface = commands.getoutput("cat /proc/net/route" \
                               "|cut -f1,2" \
                               "|grep 00000000" \
                               "|cut -f1") \
            or "lo"

    # get the IP of the interface
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', iface[:15])
    )[20:24])



def send_datagram(host, port, data):

    def do_send(host, port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.sendto(data, (host, port))
        sock.close()
        
    t = threading.Thread(target = do_send, args = [host, port, data])
    t.setDaemon(True)
    t.start()



def parse_http(data):

    if (not "\r\n\r\n" in data): return None
    
    complete = False
    
    idx = data.find("\r\n\r\n")
    hdata = data[:idx]
    body = data[idx + 4:]
    method, path, protocol, headers = parse_http_headers(hdata)

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
            body = unchunk_payload(body)

        return (method, path, protocol, headers, body)
    else:
        return None



def parse_http_headers(hdata):

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



def unchunk_payload(chunked_body):

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

