from SSDPMonitor import SSDPMonitor


def get_classes():

    return [SSDPMonitor]


messages = [
    "SSDP_ACT_SEARCH_DEVICES",
    
    "SSDP_EV_DEVICE_DISCOVERED",   # (uuid, DeviceDescription)
    "SSDP_EV_DEVICE_GONE",         # (uuid)
]

