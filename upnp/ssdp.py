"""
Lowlevel SSDP functions.
"""

from utils import logging
from utils import network


SSDP_IP = "239.255.255.250"
SSDP_PORT = 1900

_M_SEARCH = "M-SEARCH * HTTP/1.1\r\n" \
            "HOST: 239.255.255.250:1900\r\n" \
            "MAN: \"ssdp:discover\"\r\n" \
            "MX: 5\r\n" \
            "ST: upnp:rootdevice\r\n" \
            "\r\n"

_SSDP_ALIVE = "NOTIFY * HTTP/1.1\r\n" \
              "HOST:239.255.255.250:1900\r\n" \
              "CACHE-CONTROL: max-age = %d\r\n" \
              "LOCATION: %s\r\n" \
              "SERVER: Linux/2.6 UPnP/1.0 MediaBox/1.0\r\n" \
              "NT: %s\r\n" \
              "USN: %s\r\n" \
              "NTS: ssdp:alive\r\n" \
              "X-MEDIABOX-IGNORE: %s\r\n" \
              "\r\n"

_SSDP_BYEBYE = "NOTIFY * HTTP/1.1\r\n" \
               "HOST:239.255.255.250:1900\r\n" \
               "NT: %s\r\n" \
               "USN: %s\r\n" \
               "NTS: ssdp:byebye\r\n" \
               "\r\n"

_M_SEARCH_RESPONSE = "HTTP/1.1 200 OK\r\n" \
                     "CACHE-CONTROL: max-age = %d\r\n" \
                     "EXT:\r\n" \
                     "LOCATION: %s\r\n" \
                     "SERVER: Linux/2.6 UPnP/1.0 MediaBox/1.0\r\n" \
                     "ST: %s\r\n" \
                     "USN: %s\r\n" \
                     "X-MEDIABOX-IGNORE: %s\r\n" \
                     "\r\n"

SSDP_ALIVE = 0
SSDP_BYEBYE = 1


def broadcast_alive(location, notification_type, unique_service_name,
                 max_age = 1800):
    """
    Broadcasts a SSDP ALIVE notification.
    @since: 2010.10.03
    """

    data = _SSDP_ALIVE % (max_age, location, notification_type, 
                          unique_service_name, network.get_ip())
    network.send_datagram(SSDP_IP, SSDP_PORT, data)
    return max_age


def broadcast_byebye(notification_type, unique_service_name):
    """
    Broadcasts a SSDP BYE-BYE notification.
    @since: 2010.10.03
    """

    data = _SSDP_BYEBYE % (notification_type, unique_service_name)
    network.send_datagram(SSDP_IP, SSDP_PORT, data)


def broadcast_msearch(sock):
    """
    Broadcasts a SSDP M-SEARCH message.
    @since: 2010.10.03
    """
    
    data = _M_SEARCH
    print "sending M-SEARCH"
    sock.sendto(data, (SSDP_IP, SSDP_PORT))


def respond_to_msearch(host, port,
                       location, search_target, unique_service_name,
                       max_age = 1800):
    """
    Sends a response to the sender of a M-SEARCH message.
    """

    data = _M_SEARCH_RESPONSE % (max_age, location, search_target,
                                 unique_service_name, network.get_ip())
    network.send_datagram(host, port, data)
    return max_age



def parse_max_age(cache_control):

    max_age = 1800
    value = cache_control.upper()
    idx = value.find("MAX-AGE")
    if (idx >= 0):
        idx2 = value.find("=", idx)
        try:
            max_age = int(value[idx2 + 1:])
        except:
            pass
    #end if
    
    return max_age


"""
def open_sockets():
    ""
    Opens and returns the SSDP notification and discover sockets.
    If the sockets are already open, they are just returned.
    @since: 0.96
    
    @return: notification socket
    @return: discovery socket
    ""
    global _ssdp_socket, _discover_socket

    if (not _ssdp_socket):
        try:
            _ssdp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                         socket.IPPROTO_UDP)
            _ssdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            _ssdp_socket.bind((_SSDP_IP, _SSDP_PORT))
        except:
            logging.warning("cannot open socket for SSDP monitoring\n%s",
                            logging.stacktrace())
            
    if (not _discover_socket):
        try:
            _discover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            logging.warning("cannot open socket for SSDP discovering\n%s",
                            logging.stacktrace())
    
    return (_ssdp_socket, _discover_socket)
"""


"""
def discover_devices():
    ""
    Sends a M-SEARCH for discovering all available UPnP devices.
    @since: 0.96
    ""
    
    try:
        _discover_socket.sendto(_M_SEARCH, (_SSDP_IP, _SSDP_PORT))
    except:
        logging.warning("could not search for UPnP devices\n%s",
                        logging.stacktrace())
"""


"""
def __parse_ssdp_event(data):

    event = ""

    lines = data.splitlines()
    method = lines[0].upper()
    logging.debug("SSDP notification:\n%s" % data)

    if (method.startswith("NOTIFY ") or method.startswith("HTTP/")):    
        values = {}
        for l in lines[1:]:
            idx = l.find(":")
            key = l[:idx].strip().upper()
            value = l[idx + 1:].strip()
            values[key] = value
        #end for

        if ("NTS" in values):
            if (values["NTS"] == "ssdp:alive"):
                event = SSDP_ALIVE
            elif (values["NTS"] == "ssdp:byebye"):
                event = SSDP_BYEBYE
        else:
            event = SSDP_ALIVE
            
        max_age = 1800
        if ("CACHE-CONTROL" in values):
            value = values["CACHE-CONTROL"].upper()
            idx = value.find("MAX-AGE")
            if (idx >= 0):
                idx2 = value.find("=", idx)
                try:
                    max_age = int(value[idx2 + 1:])
                except:
                    pass
                    max_age = 1800
            #end if
        #end if
            
        return (event, values.get("LOCATION", ""), values["USN"], max_age)
        
    else:
        return None
"""

"""
def poll_event(sock):
    ""
    Polls for SSDP notifications on the given socket and returns an SSDP
    event tuple (event, location, usn, max_age) or None if no event was
    available.
    @since: 0.96
    ""

    try:
        data, addr = sock.recvfrom(1024)
    except socket.error:
        return None

    return __parse_ssdp_event(data)
"""

"""
_ssdp_socket = None
_discover_socket = None
"""
