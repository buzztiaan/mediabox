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

    logging.debug("[ssdp] broadcasting ALIVE")
    data = _SSDP_ALIVE % (max_age, location, notification_type, 
                          unique_service_name, network.get_ip())
    network.send_datagram(SSDP_IP, SSDP_PORT, data)
    return max_age


def broadcast_byebye(notification_type, unique_service_name):
    """
    Broadcasts a SSDP BYE-BYE notification.
    @since: 2010.10.03
    """

    logging.debug("[ssdp] broadcasting BYE-BYE")
    data = _SSDP_BYEBYE % (notification_type, unique_service_name)
    network.send_datagram(SSDP_IP, SSDP_PORT, data)


def broadcast_msearch(sock):
    """
    Broadcasts a SSDP M-SEARCH message.
    @since: 2010.10.03
    """
    
    data = _M_SEARCH
    logging.debug("[ssdp] broadcasting M-SEARCH")
    sock.sendto(data, (SSDP_IP, SSDP_PORT))


def respond_to_msearch(host, port,
                       location, search_target, unique_service_name,
                       max_age = 1800):
    """
    Sends a response to the sender of a M-SEARCH message.
    """

    logging.debug("[ssdp] M-SEARCH response to: %s:%d", host, port)
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

