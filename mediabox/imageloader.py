from io import Downloader
from utils import logging

import gobject
import gtk

_CHUNK_SIZE = 65536



def load_data(data, cb, *args):
    """
    Loads the given image data and passes a pixbuf object to the callback,
    or None if the image could not be loaded.
    """
    
    def finish_loading(loader):
        try:
            loader.close()
            if (not aborted[0]):
                pbuf = loader.get_pixbuf()
                del loader
                if (pbuf):
                    cb(pbuf, *args)
                    del pbuf
                else:
                    cb(None, *args)
            #end if
        except:
            logging.error("error\n%s", logging.stacktrace())
            cb(None, *args)
            
            
    def on_size_available(loader, width, height):
        #factor = 1
        #factor1 = 160 / float(width)
        #factor2 = 120 / float(height)
        #factor = min(factor1, factor2)
        #loader.set_size(int(width * factor), int(height * factor))

        if (width * height > 8000000):
            logging.info("aborted thumbnailing image %s because resolution is"
                         " too high: %dx%d, %0.2f megapixels",
                         path, width, height, width * height / 1000000.0)
            aborted[0] = True


    aborted = [False]
    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)
    loader.write(data)
    finish_loading(loader)



def load(path, cb, *args):
    """
    Loads the given image file and passes a pixbuf object to the callback,
    or None if the image could not be loaded.
    """

    def finish_loading(loader):
        try:
            loader.close()
            if (not aborted[0]):
                pbuf = loader.get_pixbuf()
                del loader
                if (pbuf):
                    cb(pbuf, *args)
                    del pbuf
                else:
                    cb(None, *args)
            #end if
        except:
            logging.error("error\n%s", logging.stacktrace())
            cb(None, *args)
            

    def load_cb(d, amount, total):

        if (d):
            if (not aborted[0]):
                try:
                    loader.write(d)
                except:
                    pass
        else:
            try:
                fd.close()
            except:
                pass
                
            finish_loading(loader)


    def on_size_available(loader, width, height):
        #factor = 1
        #factor1 = 160 / float(width)
        #factor2 = 120 / float(height)
        #factor = min(factor1, factor2)
        #loader.set_size(int(width * factor), int(height * factor))

        if (width * height > 8000000):
            logging.info("aborted loading image %s because resolution is"
                         " too high: %dx%d, %0.2f megapixels",
                         path, width, height, width * height / 1000000.0)
            aborted[0] = True


    aborted = [False]
    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)
    dl = Downloader(path, load_cb)

