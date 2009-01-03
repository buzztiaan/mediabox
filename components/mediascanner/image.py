import thief
from utils import logging

import os
import gtk
import threading


def is_media(f):

    return f.mimetype.startswith("image/")



def make_thumbnail_async(f, dest, cb):

    def finish_loading(loader):
        try:
            loader.close()
            if (not aborted[0]):
                pbuf = loader.get_pixbuf()
                del loader
                if (pbuf):
                    pbuf.save(dest, "jpeg")
                del pbuf
            #end if
        except:
            import traceback; traceback.print_exc()
        try:
            cb()
        except:
            logging.error("error\n%s", logging.stacktrace())


    def on_data(d, amount, total, loader):

        if (d):
            if (not aborted[0]):
                loader.write(d)
        else:
            finish_loading(loader)

    def on_size_available(loader, width, height):
        factor = 1
        factor1 = 160 / float(width)
        factor2 = 120 / float(height)
        factor = min(factor1, factor2)
        loader.set_size(int(width * factor), int(height * factor))

        if (width * height > 8000000):
            logging.info("aborted thumbnailing image %s because resolution is"
                         " too high: %dx%d, %0.2f megapixels",
                         f, width, height, width * height / 1000000.0)
            aborted[0] = True


        
    aborted = [False]
    uri = f.resource
    uri = thief.steal_image(uri) or uri

    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)
    f.load(0, on_data, loader)


        
"""
def make_thumbnail(f, dest):

    def on_data(d, amount, total, loader, finished):
        if (d):
            loader.write(d)
        else:
            finished.set()


    def on_size_available(loader, width, height):
        factor = 1
        factor1 = 160 / float(width)
        factor2 = 120 / float(height)
        factor = min(factor1, factor2)
        loader.set_size(int(width * factor), int(height * factor))    


    
    uri = f.resource
    uri = thief.steal_image(uri) or uri
    

    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)

    finished = threading.Event()
    f.load(0, on_data, loader, finished)
    while (not finished.isSet()):
        gtk.main_iteration(False)    

    try:
        loader.close()
        pbuf = loader.get_pixbuf()
        del loader
        pbuf.save(dest, "jpeg")
        del pbuf
    except:
        import traceback; traceback.print_exc()
        pass
"""
