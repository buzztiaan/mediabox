import thief

import os
import gtk


def is_media(f):

    return f.mimetype.startswith("image/")
        
        
def make_thumbnail(f, dest):
    
    uri = f.resource
    uri = thief.steal_image(uri) or uri
    
    def on_size_available(loader, width, height):
        factor = 1
        factor1 = 160 / float(width)
        factor2 = 120 / float(height)
        factor = min(factor1, factor2)
        loader.set_size(int(width * factor), int(height * factor))    

    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)
    fd = f.get_fd()
    while (True):
        data = fd.read(50000)            
        if (data):
            loader.write(data)
        else:
            break
    #end while
    fd.close()
    try:
        loader.close()
        pbuf = loader.get_pixbuf()
        del loader
        pbuf.save(dest, "jpeg")
        del pbuf
    except:
        import traceback; traceback.print_exc()
        pass

