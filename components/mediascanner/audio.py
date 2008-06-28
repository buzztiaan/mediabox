from mediaplayer import AUDIO_FORMATS
import thief

import os
import gtk



def is_media(f):

    if (f.mimetype != f.DIRECTORY):
        return False
        
    for c in f.get_children():
        if (c.mimetype.startswith("audio/")):
            f.mimetype = "audio/x-music-folder"
            return True
    #end for
    
    return False
        
        
def make_thumbnail(f, dest):

    # look for an easy-to-steal cover
    cover = thief.steal_cover(f.resource)
    contents = []
    
    # look for a cover file    
    if (not cover):
        contents = f.get_children()
        candidates = (".folder.png", "folder.jpg", "cover.jpg",
                      "cover.jpeg", "cover.png")
        for c in contents:
            print c.name
            if (c.name in candidates):
                cover = c
                break
        #end for
    #end if
    
    if (not cover):
        for c in contents:
            if (c.mimetype.startswith("image/")):
                cover = c
        #end for
    #end if

    # look for an embedded cover
    if (not cover):
        pbuf = __find_embedded_cover(contents)
        
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
    fd = cover.get_fd()
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


def __find_embedded_cover(contents):

    import idtags
    
    for c in contents[:10]:
        if (c.mimetype.startswith("audio/")):
            tags = idtags.read(c.resource)
            if ("PICTURE" in tags):
                return __load_apic(tags["PICTURE"])
        #end if
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
    