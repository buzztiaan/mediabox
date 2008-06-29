from SSDPMonitor import SSDPMonitor


def get_classes():

    return [SSDPMonitor]


messages = [
    "SSDP_EV_DEVICE_DISCOVERED",   # (uuid, servicetype, location, descr_dom)
    "SSDP_EV_DEVICE_GONE",         # (uuid)
    
    "SSDP_SVC_SUBSCRIBE", # TODO: UPnP event subscription
]

