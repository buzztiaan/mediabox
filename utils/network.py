import urlparse
import commands
import fcntl
import socket
import struct


def parse_addr(addr):
    """
    Splits the given address URL into a tuple
    C{(host, port, path)}.
    
    @param addr: address URL
    @return: C{(host, port, path)}
    """
        
    urlparts = urlparse.urlparse(addr)
    
    netloc = urlparts.netloc.split(":")[0]
    path = urlparts.path
    if (urlparts.query):
        path += "?" + urlparts.query
    return (netloc, int(urlparts.port or 0), path)


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

