import urlparse
import commands
import fcntl
import socket
import struct


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
        self.port = parts.port
        self.netloc = parts.netloc
        self.path = parts.path or 80
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

