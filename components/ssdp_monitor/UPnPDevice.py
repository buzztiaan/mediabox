from device import Device, File
from upnp.MiniXML import MiniXML
from upnp.SOAPProxy import SOAPProxy
from upnp import didl_lite
from utils import logging

import urllib
import urlparse
import os
import gtk


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"


class UPnPDevice(Device):
    """
    Class representing a UPnP device with ContentDirectory.
    """

    def __init__(self, location):
        """
        Builds a new UPnP device object from the given description URL.
        """
    
        # cache for DIDL responses
        self.__didl_cache = {}
    
        self.__location = location
        
        self.__device_type = ""
        self.__udn = ""
        self.__friendly_name = ""
        self.__manufacturer = ""
        self.__model_name = ""
        self.__model_number = ""
        self.__model_description = ""
        self.__presentation_url = "" 
        self.__url_base = ""
        
        self.__icon_url = ""
        
        self.__cds_proxy = None


        Device.__init__(self)
        self.__parse_description(location)


            
    def __parse_description(self, location):
    
        logging.info("loading UPnP device description '%s'", location)
        xml = urllib.urlopen(location).read()
        dom = MiniXML(xml, _NS_DESCR).get_dom()
        self.__url_base = dom.get_pcdata("{%s}URLBase" % _NS_DESCR).strip()
        if (not self.__url_base):
            self.__url_base = self.__location[:self.__location.rfind("/")]
        
        device = dom.get_child("{%s}device" % _NS_DESCR)
        self.__device_type = device.get_pcdata("{%s}deviceType" % _NS_DESCR)
        self.__udn = device.get_pcdata("{%s}UDN" % _NS_DESCR)
        self.__friendly_name = device.get_pcdata("{%s}friendlyName" % _NS_DESCR)
        self.__manufacturer = device.get_pcdata("{%s}manufacturer" % _NS_DESCR)
        self.__model_name = device.get_pcdata("{%s}modelName" % _NS_DESCR)
        self.__model_number = device.get_pcdata("{%s}modelNumber" % _NS_DESCR)
        self.__model_description = device.get_pcdata("{%s}modelDescription" % _NS_DESCR)
        self.__presentation_url = device.get_pcdata("{%s}presentationURL" % _NS_DESCR)

        svclist = device.get_child("{%s}serviceList" % _NS_DESCR)
        for service in svclist.get_children():
            svctype = service.get_pcdata("{%s}serviceType" % _NS_DESCR)
            scpd_url = urlparse.urljoin(self.__url_base,
                                 service.get_pcdata("{%s}SCPDURL" % _NS_DESCR))
            ctrl_url = urlparse.urljoin(self.__url_base,
                              service.get_pcdata("{%s}controlURL" % _NS_DESCR))
      
            
            if (svctype == "urn:schemas-upnp-org:service:ContentDirectory:1" or
                svctype == "urn:schemas-upnp-org:service:ContentDirectory:2"):
                self.__cds_proxy = SOAPProxy(ctrl_url, svctype, scpd_url)

        #end for

        # load icon if available
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
        
            # sort by size (and eventually mimetype because we should prefer PNG)
            return cmp(area1, area2)

        icons = node.get_children()
        icons.sort(icon_comparator)
        preferred_icon = icons[-1]
        
        return preferred_icon.get_pcdata("{%s}url" % _NS_DESCR)


    def has_content_directory(self):
    
        return (self.__cds_proxy != None)


    def get_icon(self):

        if (self.__icon_url):
            loader = gtk.gdk.PixbufLoader()
            loader.write(urllib.urlopen(self.__icon_url).read())
            loader.close()
            icon = loader.get_pixbuf()
            del loader
        else:
            icon = None
           
        return icon

        
    def get_name(self):
    
        return self.__friendly_name
        
        
    def get_root(self):
    
        return "0"
        
        
    def ls(self, path):
    
        try:
            didl = self.__didl_cache[path]
        except KeyError:
            didl, nil, nil, nil = self.__cds_proxy.Browse(path,
                                                "BrowseDirectChildren",
                                                "*", "0", "0", "")
            self.__didl_cache[path] = didl
            
        files = []
        for entry in didl_lite.parse(didl):
            ident, clss, child_count, res, title, artist = entry
            f = File()
            f.name = title
            f.info = artist
            f.filetype = clss.startswith("object.container") \
                       and f.DIRECTORY or f.FILE
            if (f.filetype == f.DIRECTORY):
                f.path = ident
            else:
                f.path = urlparse.urljoin(self.__url_base, res)
            f.child_count = child_count
            files.append(f)
            
        return files



if (__name__ == "__main__"):   
    dev = UPnPDevice("http://192.168.0.102:49152/description.xml")
    dev.ls("1")

