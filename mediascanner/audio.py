import os
import gtk


_MUSIC_EXT = (".mp3", ".wav", ".wma", ".ogg",
              ".aac", ".flac", ".m4a")


def is_media(uri):

    try:
        if (not os.path.isdir(uri)):
            return False
        
        files = os.listdir(uri)
        for f in files:
            ext = os.path.splitext(f)[1]
            if (ext.lower() in _MUSIC_EXT):
                return True
        #end for
    except:
        pass
        
    return False
        
        
def make_thumbnail(uri, dest):

    candidates = [ os.path.join(uri, ".folder.png"),
                    os.path.join(uri, "cover.jpg"),
                    os.path.join(uri, "cover.jpeg"),
                    os.path.join(uri, "cover.png") ]

    imgs = [ os.path.join(uri, f)
                for f in os.listdir(uri)
                if f.lower().endswith(".png") or
                f.lower().endswith(".jpg") ]

    cover = ""
    for c in candidates + imgs:
        if (os.path.exists(c)):
            cover = c
            break
    #end for

    if (not cover): return

    def on_size_available(loader, width, height):
        factor = 1
        factor1 = 160 / float(width)
        factor2 = 120 / float(height)
        factor = min(factor1, factor2)
        loader.set_size(int(width * factor), int(height * factor))    

    loader = gtk.gdk.PixbufLoader()
    loader.connect("size-prepared", on_size_available)
    fd = open(cover, "r")
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

