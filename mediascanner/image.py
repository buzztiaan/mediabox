import os
import gtk


_IMAGE_EXT = (".bmp", ".gif", ".jpg", ".jpeg", ".png", ".svg", ".xpm")


def is_media(uri):

    try:
        if (os.path.isdir(uri)):
            return False
        
        # ignore 'cover.jpg'
        if (uri.endswith("/cover.jpg")):
            return False

        elif (os.path.splitext(uri)[1].lower() in _IMAGE_EXT):
            return True
            
    except:
        return False
        
        
def make_thumbnail(uri, dest):
    
    def on_size_available(loader, width, height):
        factor = 1
        factor1 = 160 / float(width)
        factor2 = 120 / float(height)
        factor = min(factor1, factor2)
        loader.set_size(int(width * factor), int(height * factor))    

    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)
    fd = open(uri, "r")
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

