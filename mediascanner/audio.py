import thief

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

    # look for an easy-to-steal cover
    cover = thief.steal_cover(uri)
    
    # look for a cover file
    if (not cover):
        candidates = [ os.path.join(uri, ".folder.png"),
                        os.path.join(uri, "cover.jpg"),
                        os.path.join(uri, "cover.jpeg"),
                        os.path.join(uri, "cover.png") ]

        imgs = [ os.path.join(uri, f)
                    for f in os.listdir(uri)
                    if f.lower().endswith(".png") or
                    f.lower().endswith(".jpg") ]

        for c in candidates + imgs:
            if (os.path.exists(c)):
                cover = c
                break
        #end for
    #end if

    # look for an embedded cover
    if (not cover):
        pbuf = __find_embedded_cover(uri)
        
    else:
        pbuf = __load_pbuf(cover)

    if (pbuf):
        pbuf.save(dest, "jpeg")
        del pbuf
        
        
def __load_pbuf(cover):        

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
        return pbuf
    except:
        import traceback; traceback.print_exc()
        return None


def __find_embedded_cover(uri):

    import idtags
    
    dirpath = uri #os.path.dirname(uri)
    cnt = 0
    for f in os.listdir(dirpath):
        ext = os.path.splitext(f)[1]
        if (not ext.lower() in _MUSIC_EXT): continue
        if (cnt == 10): break
        
        tags = idtags.read(os.path.join(dirpath, f))
        if ("PICTURE" in tags):
            return __load_apic(tags["PICTURE"])
        cnt += 1
    #end for
    
    return None
    
    
def __load_apic(data):

    def on_size_available(loader, width, height):
        factor = 1
        factor1 = 160 / float(width)
        factor2 = 120 / float(height)
        factor = min(factor1, factor2)
        loader.set_size(int(width * factor), int(height * factor))

    idx = data.find("\x00", 1)
    idx = data.find("\x00", idx + 1)
    while (data[idx] == "\x00"): idx += 1
    
    picdata = data[idx:]

    try:
        loader = gtk.gdk.PixbufLoader()
        loader.connect("size-prepared", on_size_available)
        loader.write(picdata)
        loader.close()
        pbuf = loader.get_pixbuf()
    except:
        import traceback; traceback.print_exc()
        pbuf = None
        
    return pbuf
    
