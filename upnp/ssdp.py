from utils import logging
import socket
import time


_SSDP_IP = "239.255.255.250"
_SSDP_PORT = 1900
_M_SEARCH = "M-SEARCH * HTTP/1.1\r\n" \
            "MX: 5\r\n" \
            "HOST: 239.255.255.250:1900\r\n" \
            "MAN: \"ssdp:discover\"\r\n" \
            "ST: upnp:rootdevice\r\n" \
            "\r\n"


SSDP_ALIVE = 0
SSDP_BYEBYE = 1



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



def poll_event():
    global _discover_time

    if (not _ssdp_socket): _open_sockets()
    try:
        data, addr = _ssdp_socket.recvfrom(1024)
    except socket.error:
        try:
            data, addr = _discover_socket.recvfrom(1024)
        except socket.error:
            return None

    if (_discover_time > 0 and time.time() > _discover_time + 10):
        _discover_time = 0
        _discover_socket.close()

    return __parse_ssdp_event(data)


def _open_sockets():
    global _ssdp_socket, _discover_socket, _discover_time

    try:
        _ssdp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        _ssdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _ssdp_socket.bind((_SSDP_IP, _SSDP_PORT))
        _ssdp_socket.setblocking(False)
    except:
        logging.warning("cannot open socket for SSDP monitoring")
        import traceback; traceback.print_exc()

    try:
        _discover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _discover_socket.setblocking(False)
        _discover_socket.sendto(_M_SEARCH, (_SSDP_IP, _SSDP_PORT))
        _discover_time = time.time()
    except:
        logging.warning("cannot open socket for SSDP discovering")
        import traceback; traceback.print_exc()

    


_ssdp_socket = None
_discover_socket = None
_discover_time = 0
_open_sockets()

