"""
UPnP device description.
"""

from SOAPProxy import SOAPProxy
from GenaSocket import GenaSocket
from utils import logging

import urlparse


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"


class DeviceDescription(object):
    """
    Class for representing a UPnP device description. The service proxies are
    being loaded when needed to minimize load and memory consumption in an
    environment with many UPnP devices where we may not be interested in most
    of them.
    """
    
    def __init__(self, location, dom):
        """
        Creates a new DeviceDescription object from the given DOM tree of a
        device description.
        
        @param location: URL of the device location
        @param dom: the DOM tree of the description XML (see L{utils.MiniXML})
        """
        
        self.__dom = dom
        
        # location of the device description
        self.__location = location
        
        # prefix for accessing relative URLs
        self.__url_base = ""

        self.__device_type = ""
        self.__udn = ""
        self.__friendly_name = ""
        self.__manufacturer = ""
        self.__model_name = ""
        self.__model_number = ""
        self.__model_description = ""
        self.__presentation_url = "" 
        self.__url_base = ""
        
        # mapping of service type to (SCPDURL, controlURL, eventSubURL)
        self.__services = {}

        # mapping of service type to a SOAP proxy
        self.__service_proxies = {}
        

        self.__icon_url = ""
        
        try:
            self.__parse_description(dom)
        except:
            import traceback; traceback.print_exc()
        
        
        
    def __parse_description(self, dom):
    
        print "parse descr"
        self.__url_base = dom.get_pcdata("{%s}URLBase" % _NS_DESCR).strip()
        if (not self.__url_base):
            # some devices make life hard and don't tell about their URL base
            self.__url_base = self.__location[:self.__location.rfind("/")]

        # read device information
        device = dom.get_child("{%s}device" % _NS_DESCR)
        self.__device_type = device.get_pcdata("{%s}deviceType" % _NS_DESCR)
        self.__udn = device.get_pcdata("{%s}UDN" % _NS_DESCR)
        self.__friendly_name = device.get_pcdata("{%s}friendlyName" % _NS_DESCR)
        self.__manufacturer = device.get_pcdata("{%s}manufacturer" % _NS_DESCR)
        self.__model_name = device.get_pcdata("{%s}modelName" % _NS_DESCR)
        self.__model_number = device.get_pcdata("{%s}modelNumber" % _NS_DESCR)
        self.__model_description = device.get_pcdata("{%s}modelDescription" % _NS_DESCR)
        self.__presentation_url = device.get_pcdata("{%s}presentationURL" % _NS_DESCR)

        # read services
        svclist = device.get_child("{%s}serviceList" % _NS_DESCR)
        for service in svclist.get_children():
            svctype = service.get_pcdata("{%s}serviceType" % _NS_DESCR)
            scpd_url = urlparse.urljoin(self.__url_base,
                                  service.get_pcdata("{%s}SCPDURL" % _NS_DESCR))
            ctrl_url = urlparse.urljoin(self.__url_base,
                               service.get_pcdata("{%s}controlURL" % _NS_DESCR))
            event_url = urlparse.urljoin(self.__url_base,
                              service.get_pcdata("{%s}eventSubURL" % _NS_DESCR))
            
            self.__services[svctype] = (scpd_url, ctrl_url, event_url)
            
            # we use lazy loading for the SOAP proxy, so we don't create it now
            
        #end for
        # read icon if available
        icons = device.get_child("{%s}iconList" % _NS_DESCR)
        if (icons):
            self.__icon_url = urlparse.urljoin(self.__url_base,
                                               self.__load_icon(icons))


    def __load_icon(self, node):
        
        def icon_comparator(icon1, icon2):
            mimetype1 = icon1.get_pcdata("{%s}mimetype" % _NS_DESCR)
            width1 = int(icon1.get_pcdata("{%s}width" % _NS_DESCR))
            height1 = int(icon1.get_pcdata("{%s}height" % _NS_DESCR))
            area1 = width1 * height1

            mimetype2 = icon2.get_pcdata("{%s}mimetype" % _NS_DESCR)
            width2 = int(icon2.get_pcdata("{%s}width" % _NS_DESCR))
            height2 = int(icon2.get_pcdata("{%s}height" % _NS_DESCR))
            area2 = width2 * height2

            # sort by mimetype and size (PNG is preferred because it
            # supports transparency)
            if (mimetype1 == mimetype2):
                return cmp(area1, area2)
            else:
                if (mimetype1 == "image/png"):
                    return 1
                else:
                    return -1
            #end if        

        icons = node.get_children()
        icons.sort(icon_comparator)
        preferred_icon = icons[-1]

        return preferred_icon.get_pcdata("{%s}url" % _NS_DESCR)


    def get_url_base(self):
        """
        Returns the URL base used by the device.
        
        @return: URL base
        """
        
        return self.__url_base


    def get_friendly_name(self):
        """
        Returns the friendly (i.e. human readable) name of the device.
        
        @param: human readable name of device
        """
    
        return self.__friendly_name


    def get_icon_url(self, ideal_width, ideal_height):
        """
        Returns the URL of an icon which matches the given size best.
        Returns an empty string if the device has no icons.
        
        @param ideal_width: desired width
        @param ideal_height: desired height
        @return: URL of icon on the device
        
        @todo: width and height are currently ignored
        """
        
        # TODO: find best match
        return self.__icon_url


    def get_device_type(self):
        """
        Returns the type of device.
        
        @return: UPnP device type
        """
        
        return self.__device_type
        
        
    def get_udn(self):
        """
        Returns the UDN of the device.
        
        @return: UDN string
        """
        
        return self.__udn
        
        
    def get_model_description(self):
        """
        Returns the model description text.
        
        @return: human readable model description
        """
        
        return self.__model_description
        
        
    def get_presentation_url(self):
        """
        Returns the presentation URL of the device. This is typically the
        URL of a web interface provided by the device.
        
        @return: URL of presentation interface
        """
        
        return self.__presentation_url
        
        
    def list_services(self):
        """
        Returns a list of the supported services.
        
        @return: list of services
        """
        
        return self.__services.keys()
        
        
    def get_service_proxy(self, service):
        """
        Returns the service proxy object for the given service.
        
        @return: SOAP proxy object (see L{upnp.SOAPProxy})
        @raise KeyError: if the service is not supported
        """
    
        # lazy loading of the SOAP proxy
        try:
            proxy = self.__service_proxies[service]
        except KeyError:
            try:
                scpd_url, ctrl_url, event_url = self.__services[service]
                proxy = SOAPProxy(ctrl_url, service, scpd_url)
                self.__service_proxies[service] = proxy
            except KeyError:
                return None
            
        return proxy
        
        
    def subscribe(self, service, cb):
        """
        Subscribes to the given service and registers a callback for
        handling incoming events on this URL.
        
        @todo: describe signature of callback
        
        @param service: service
        @param cb: callback function
        """

        scpd_url, ctrl_url, ev_url = self.__services[service]
        gena = GenaSocket()
        gena.subscribe(ev_url, cb)
        
        
    def unsubscribe(self, cb):
        """
        Unsubscribes the given callback.
        
        @param cb: callback function
        """
        
        gena = GenaSocket()
        gena.unsubscribe(cb)



    def _dump_xml(self):
        """
        Dumps the description XML.
        """
        
        logging.debug("Device Description [%s]\n%s" \
                      % (self.__location, self.__dom._dump()))

