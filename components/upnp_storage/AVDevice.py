from storage import Device, File
from io import SeekableFD
from io import Downloader
from utils.MiniXML import MiniXML
from upnp.SOAPProxy import SOAPProxy
from upnp import didl_lite
from utils import mimetypes
from utils import logging
import theme

import urllib
import urlparse
import os
import gtk


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"
_SERVICE_CONTENT_DIRECTORY_1 = "urn:schemas-upnp-org:service:ContentDirectory:1"
_SERVICE_CONTENT_DIRECTORY_2 = "urn:schemas-upnp-org:service:ContentDirectory:2"


class AVDevice(Device):
    """
    Class representing a UPnP device with ContentDirectory.
    """

    CATEGORY = Device.CATEGORY_LAN
    TYPE = Device.TYPE_GENERIC
    

    # supported UPnP device types
    DEVICE_TYPES = ["urn:schemas-upnp-org:device:MediaServer:1",
                    "urn:schemas-upnp-org:device:MediaServer:2"]


    def __init__(self, descr):
        """
        Builds a new UPnP device object from the given description URL.
        """

        self.__description = descr
        self.__icon = None
    
        # cache for DIDL responses
        self.__didl_cache = {}

        dtype = descr.get_device_type()
        if (dtype == "urn:schemas-upnp-org:device:MediaServer:1"):
            svc = _SERVICE_CONTENT_DIRECTORY_1
        elif (dtype == "urn:schemas-upnp-org:device:MediaServer:2"):
            svc = _SERVICE_CONTENT_DIRECTORY_2
        else:
            svc = None

        if (svc):
            try:
                self.__cds_proxy = descr.get_service_proxy(svc)
            except KeyError:
                self.__cds_proxy = None

        Device.__init__(self)



    def get_prefix(self):
    
        return "upnp://%s" % self.__description.get_udn()


    def get_icon(self):

        if (not self.__icon):
            icon_url = self.__description.get_icon_url(96, 96)
            if (icon_url):
                loader = gtk.gdk.PixbufLoader()
                loader.write(urllib.urlopen(icon_url).read())
                loader.close()
                self.__icon = loader.get_pixbuf()
                del loader
            else:
                self.__icon = theme.mb_device_unknown
           
        return self.__icon

        
    def get_name(self):
    
        return self.__description.get_friendly_name()
        
        
    def get_root(self):
    
        f = File(self)
        f.path = "0"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        
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
        f.artist = artist
        f.info = artist

        if (f.mimetype == f.DIRECTORY):
            f.path = "/" + ident
        else:
            f.path = "/" + ident
                        
        if (f.mimetype in ["application/octet-stream"]):
            ext = os.path.splitext(f.name)[-1]
            f.mimetype = mimetypes.lookup_ext(ext)
            
        f.child_count = child_count    
        
        # MythTV thinks Ogg-Vorbis was text/plain...
        if (clss.startswith("object.item.audioItem") and
            f.mimetype == "text/plain"):
            f.mimetype = "audio/x-unknown"
            
        logging.debug("'%s' has MIME type '%s'" % (f.name, f.mimetype))
        
        return f


    def __get_didl(self, path):

        if (path.startswith("/")): path = path[1:]
        try:
            didl = self.__didl_cache[path]
        except KeyError:
            didl, nil, nil, nil = self.__cds_proxy.Browse(None, path,
                                                "BrowseDirectChildren",
                                                "*", "0", "0", "")
            #self.__didl_cache[path] = didl
            
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

        #path = "/11"
        def f(entry):
            if (entry):
                item = self.__build_file(url_base, entry)
            else:
                item = None
            return cb(item, *args)
            
        didl = self.__get_didl(path)
        files = []
        url_base = self.__description.get_url_base()
        didl_lite.parse_async(didl, f)


    def load(self, resource, maxlen, cb, *args):
    
        def f(d, amount, total):
            try:
                cb(d, amount, total, *args)
            except:
                pass

            if (d and maxlen > 0 and amount >= maxlen):
                try:
                    cb("", amount, total, *args)
                except:
                    pass
                dloader.cancel()
        
        
        dloader = Downloader(resource, f)
