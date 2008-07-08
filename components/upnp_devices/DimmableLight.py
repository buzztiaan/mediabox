class DimmableLight(object):

    # supported UPnP device types
    DEVICE_TYPES = ["urn:schemas-upnp-org:device:DimmableLight:1"]
    
    
    def __init__(self, descr):
    
        #descr._dump_xml()
        descr.subscribe("urn:schemas-upnp-org:service:SwitchPower:1", self.__on_switch)
        
        
    def __on_switch(self, *args):
    
        print "ON SWITCH"
        pass
