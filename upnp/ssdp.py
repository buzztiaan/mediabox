"""
Lowlevel SSDP functions.
"""

from utils import logging
import socket


_SSDP_IP = "239.255.255.250"
_SSDP_PORT = 1900
_M_SEARCH = "M-SEARCH * HTTP/1.1\r\n" \
            "HOST: 239.255.255.250:1900\r\n" \
            "MAN: \"ssdp:discover\"\r\n" \
            "MX: 5\r\n" \
            "ST: upnp:rootdevice\r\n" \
            "\r\n"


SSDP_ALIVE = 0
SSDP_BYEBYE = 1



def open_sockets():
    """
    Opens and returns the SSDP notification and discover sockets.
    If the sockets are already open, they are just returned.
    
    @return: notification socket
    @return: discovery socket
    """
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



def discover_devices():
    """
    Sends a M-SEARCH for discovering all available UPnP devices.
    """
    
    try:
        _discover_socket.sendto(_M_SEARCH, (_SSDP_IP, _SSDP_PORT))
    except:
        logging.error("could not search for UPnP devices\n%s",
                      logging.stacktrace())



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
            
        return (event, values.get("LOCATION", ""), values["USN"])
        
    else:
        return None


def poll_event(sock):
    """
    Polls for SSDP notifications on the given socket and returns an SSDP
    event tuple (event, location, usn) or None if no event was available.
    """
    try:
        data, addr = sock.recvfrom(1024)
    except socket.error:
        return None

    return __parse_ssdp_event(data)
   


_ssdp_socket = None
_discover_socket = None

