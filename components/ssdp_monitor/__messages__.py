def SSDP_ACT_SEARCH_DEVICES(): pass
"""
Instructs the SSDP monitor to search for UPnP devices.
"""

def SSDP_EV_DEVICE_DISCOVERED(uuid, device_description): pass
"""
Gets emitted when the SSDP monitor discovers a new UPnP device. The device
decription is an object of type L{upnp.DeviceDescription}.

@param uuid: UUID string of the UPnP device
@param device_description: device description object
"""

def SSDP_EV_DEVICE_GONE(uuid): pass
"""
Gets emitted when a UPnP device is gone, either by having issued bye-bye, or
by having expired.

@param uuid: UUID string of the gone UPnP device
"""

