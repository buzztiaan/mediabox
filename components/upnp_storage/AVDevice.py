from com import msgs
from storage import Device, File
from io import SeekableFD
from io import Downloader
from ui.dialog import FileDialog
from utils.MiniXML import MiniXML
from upnp.SOAPProxy import SOAPProxy
from upnp import didl_lite
from utils import mimetypes
from utils import logging
from utils import urlquote
from mediabox import values
from theme import theme

import urllib
import urlparse
import os
import gtk
import gzip
import base64


_NS_DESCR = "urn:schemas-upnp-org:device-1-0"
_SERVICE_CONTENT_DIRECTORY_1 = "urn:schemas-upnp-org:service:ContentDirectory:1"
_SERVICE_CONTENT_DIRECTORY_2 = "urn:schemas-upnp-org:service:ContentDirectory:2"

_CACHE_DIR = os.path.join(values.USER_DIR, "upnpcache")



class AVDevice(Device):
    """
    Storage device representing a UPnP device with ContentDirectory.
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

        # create cache if it does not exist yet
        if (not os.path.exists(_CACHE_DIR)):        
            try:
                os.makedirs(_CACHE_DIR)
            except:
                pass

        # clear cache of old files from previous sessions
        else:
            old_files = [ os.path.join(_CACHE_DIR, f)
                          for f in os.listdir(_CACHE_DIR)
                          if os.path.getmtime(os.path.join(_CACHE_DIR, f)) <
                             values.START_TIME ]
            for f in old_files:
                try:
                    os.unlink(f)
                except:
                    pass
        #end if


    def get_prefix(self):
    
        return "upnp://%s" % self.__description.get_udn()


    def get_icon(self):

        if (not self.__icon):
            icon_url = self.__description.get_icon_url(96, 96)
            if (icon_url):
                data = urllib.urlopen(icon_url).read()
                self.__icon = "data://" + base64.b64encode(data)
            else:
                self.__icon = theme.mb_folder_upnp_mediaserver.get_path()
           
        return self.__icon

        
    def get_name(self):
    
        return self.__description.get_friendly_name()
        
        
    def get_file(self, path):
    
        f = None
        if (path == "/"):
            f = File(self)
            f.path = "0"
            f.mimetype = f.DEVICE_ROOT
            f.resource = ""
            f.name = self.get_name()
            f.icon = self.get_icon()
            f.info = "UPnP network storage"
            f.folder_flags = f.ITEMS_ENQUEUEABLE
            
        else:
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
            f.path = "/" + path

            if (f.mimetype == f.DIRECTORY):
                f.resource = ident
                f.folder_flags = f.ITEMS_ENQUEUEABLE
            else:
                f.resource = urlparse.urljoin(url_base, res)
            f.child_count = child_count

        return f


    def __build_file(self, url_base, entry):

        ident, clss, child_count, res, title, artist, mimetype = entry
        f = File(self)
        f.mimetype = mimetype
        f.resource = res or urlparse.urljoin(url_base, ident)
        print f.resource
        f.name = title
        f.artist = artist
        f.info = artist

        if (f.mimetype == f.DIRECTORY):
            f.path = "/" + ident
            f.folder_flags = f.ITEMS_ENQUEUEABLE
        else:
            f.path = "/" + ident

        f.child_count = child_count    
        
        # MythTV thinks Ogg-Vorbis was text/plain...
        if (clss.startswith("object.item.audioItem") and
            f.mimetype == "text/plain"):
            f.mimetype = "audio/x-unknown"

        # no useful MIME type reported? let's look at the file extension
        if (not f.mimetype in mimetypes.get_audio_types() + 
                              mimetypes.get_video_types() +
                              mimetypes.get_image_types() + [f.DIRECTORY]):
            ext = os.path.splitext(f.name)[-1]
            f.mimetype = mimetypes.ext_to_mimetype(ext)

        if (f.mimetype.startswith("image/")):
            f.thumbnail = f.resource
            
        logging.debug("'%s' has MIME type '%s'" % (f.name, f.mimetype))
        
        return f


    def __get_didl(self, path):
       
        if (path.startswith("/")): path = path[1:]
        
        cache_key = urlquote.quote(self.get_prefix() + "/" + path, safe = "")
        cache_file = os.path.join(_CACHE_DIR, cache_key + ".didl.gz")

        didl = None
        if (os.path.exists(cache_file)):
            try:
                didl = gzip.open(cache_file, "r").read()
            except:
                pass
        #end if        

        if (not didl):
            # hello ORB, you'd misinterpret the RequestedCount parameter,
            # so I'm feeding you an insanely high number instead of '0',
            # which was originally intended to mean "return _all_ entries"  >:(
            didl, nil, nil, nil = self.__cds_proxy.Browse(None, path,
                                                "BrowseDirectChildren",
                                                "*", "0", "50000", "")

            try:
                gzip.open(cache_file, "w").write(didl)
            except:
                pass
            
        return didl
        

    def __on_download(self, folder, f):

        dlg = FileDialog(FileDialog.TYPE_SAVE, "Save File")
        if (os.path.splitext(f.name)[1]):
            ext = ""
        else:
            ext = os.path.splitext(f.resource)[1]
        dlg.set_filename(f.name + ext)
        dlg.run()
        
        destination = dlg.get_filename()
        if (destination):
            self.call_service(msgs.DOWNLOADER_SVC_GET, f.resource,
                              destination)


    def get_file_actions(self, folder, f):

        actions = Device.get_file_actions(self, folder, f)
        if (f.mimetype != f.DIRECTORY):
            actions.append((None, "Download", self.__on_download))

        return actions
     
   
    def get_contents(self, path, begin_at, end_at, cb, *args):
    
        def f(entry, counter):
            if (entry):
                if (begin_at <= counter[0] <= end_at):
                    item = self.__build_file(url_base, entry)
                    try:
                        ret = cb(item, *args)
                    except:
                        import traceback; traceback.print_exc()
                    counter[0] += 1
                    return ret

                else:
                    counter[0] += 1
                    return True
                #end if

            else:
                cb(None, *args)
                return False
            #end if


        if (end_at == 0):
            end_at = 999999999
        didl = self.__get_didl(path.path)
        url_base = self.__description.get_url_base()
        didl_lite.parse_async(didl, f, [0])


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
        
        dloader = Downloader(resource.resource, f)

