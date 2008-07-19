from storage import Device, File
from upnp.MiniXML import MiniXML
from upnp.SOAPProxy import SOAPProxy
from upnp import didl_lite
from utils import mimetypes
from utils import logging

import urllib
import urlparse
import os
import gtk


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"
_SERVICE_CONTENT_DIRECTORY_1 = "urn:schemas-upnp-org:service:ContentDirectory:1"


class AVDevice(Device):
    """
    Class representing a UPnP device with ContentDirectory.
    """

    # supported UPnP device types
    DEVICE_TYPES = ["urn:schemas-upnp-org:device:MediaServer:1"]


    def __init__(self, descr):
        """
        Builds a new UPnP device object from the given description URL.
        """

        self.__description = descr
    
        # cache for DIDL responses
        self.__didl_cache = {}

        try:
            self.__cds_proxy = descr.get_service_proxy(_SERVICE_CONTENT_DIRECTORY_1)
        except KeyError:
            self.__cds_proxy = None

        Device.__init__(self)



    def get_prefix(self):
    
        return "upnp://%s" % self.__description.get_udn()


    def get_icon(self):

        icon_url = self.__description.get_icon_url(96, 96)
        if (icon_url):
            loader = gtk.gdk.PixbufLoader()
            loader.write(urllib.urlopen(icon_url).read())
            loader.close()
            icon = loader.get_pixbuf()
            del loader
        else:
            icon = None
           
        return icon

        
    def get_name(self):
    
        return self.__description.get_friendly_name()
        
        
    def get_root(self):
    
        f = File(self)
        f.path = "0"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = ""
        
        return f    


    def get_file(self, path):

        if (path.startswith("/")): path = path[1:]
        didl, nil, nil, nil = self.__cds_proxy.Browse(None, path,
                                                      "BrowseMetadata",
                                                      "*", "0", "0", "")
        entry = didl_lite.parse(didl)
        ident, clss, child_count, res, title, artist, mimetype = entry[0]

        url_base = self.__description.get_url_base()

        f = File(self)
        f.mimetype = mimetype
        f.resource = res
        f.name = title
        f.info = artist
        f.path = path

        if (f.mimetype == f.DIRECTORY):
            f.resource = ident
        else:
            f.resource = urlparse.urljoin(url_base, res)
        f.child_count = child_count

        return f


    def __build_file(self, url_base, entry):

        ident, clss, child_count, res, title, artist, mimetype = entry
        f = File(self)
        f.mimetype = mimetype
        f.resource = res or urlparse.urljoin(url_base, ident)
        f.name = title
        f.info = artist

        if (f.mimetype == f.DIRECTORY):
            f.path = ident
        else:
            f.path = urlparse.urljoin(url_base, res)
            
        if (f.mimetype in ["application/octet-stream"]):
            ext = os.path.splitext(f.name)[-1]
            f.mimetype = mimetypes.lookup_ext(ext)
            
        f.child_count = child_count    
        
        return f


    def __get_didl(self, path):

        if (path.startswith("/")): path = path[1:]
        try:
            didl = self.__didl_cache[path]
        except KeyError:
            didl, nil, nil, nil = self.__cds_proxy.Browse(None, path,
                                                "BrowseDirectChildren",
                                                "*", "0", "0", "")
            self.__didl_cache[path] = didl
            
        return didl
    
        
        
    def ls(self, path):
    
        didl = self.__get_didl(path)
        files = []
        url_base = self.__description.get_url_base()
        for entry in didl_lite.parse(didl):
            f = self.__build_file(url_base, entry)
            files.append(f)
            
        return files
        
        
    def ls_async(self, path, cb, *args):

        def f(entry):
            print entry       
            item = self.__build_file(url_base, entry)
            return cb(item, *args)
            
        didl = self.__get_didl(path)
        files = []
        url_base = self.__description.get_url_base()
        didl_lite.parse_async(didl, f)


    def get_fd(self, resource):
    
        fd = urllib.urlopen(resource)
        return fd


if (__name__ == "__main__"):   
    dev = UPnPDevice("http://192.168.0.102:49152/description.xml")
    dev.ls("1")

