import thief
import imageloader
from mediabox import tagreader

import os
import gtk
import threading



def is_media(f):
    
    if (f.mimetype == "application/x-music-folder"):
        return True
        
    elif (f.is_local and f.mimetype == f.DIRECTORY):
        for c in f.get_children():
            if (c.mimetype.startswith("audio/")):
                return True
        #end for        
    #end if

    return False


def make_thumbnail_async(f, dest, cb):

    if (f.mimetype == "application/x-music-folder"):
        _load_cover(f, dest, cb)
        
    elif (f.mimetype == "application/x-artist-folder"):
        _load_cover(f, dest, cb)
        
    else:
        cb()
    
    
    
def _load_cover(f, dest, cb):

    # look for an easy-to-steal cover
    cover = thief.steal_cover(f.resource)
    
    if (not cover):
        cover = _find_cover_file(f.resource)
        
    if (not cover):
        children = f.get_children()
        if (children):
            cover = _find_cover_of_file(children[0])
            if (not cover):
                _load_embedded_cover(children[0], dest, cb)
                return
            #end if
        #end if
    #end if
    
    if (cover):
        _load_cover_file(cover, dest, cb)
    else:
        cb()
   
    
def _load_cover_file(path, dest, cb):

    def on_loaded(pbuf):
        if (pbuf):
            pbuf.save(dest, "jpeg")
            del pbuf
        cb()

    imageloader.load(path, on_loaded)


def _load_embedded_cover(f, dest, cb):

    def on_loaded(pbuf):
        if (pbuf):
            pbuf.save(dest, "jpeg")
            del pbuf
        cb()

    data = _find_embedded_cover(f)
    if (data):
        imageloader.load_data(data, on_loaded)
    else:
        cb()

    
    
def _find_cover_file(uri):

    if (not uri.startswith("/") or not os.path.isdir(uri)):
        return None
        
    cover = None
    contents = os.listdir(uri)
    candidates = (".folder.png", "folder.jpg", "cover.jpg",
                    "cover.jpeg", "cover.png", "cover.bmp")
    for c in contents:
        if (c in candidates):
            cover = os.path.join(uri, c)
            break
    #end for

    if (not cover):
        for c in contents:
            cl = c.lower()
            if (cl.endswith(".jpg") or \
                  cl.endswith(".png") or \
                  cl.endswith(".jpeg") or \
                  cl.endswith(".bmp")):
                cover = os.path.join(uri, c)
                break
        #end for
    #end if

    return cover


def _find_cover_of_file(f):

    if (not f.resource.startswith("/")):
        return None
        
    parent = os.path.dirname(f.resource)
    return _find_cover_file(parent)



def _find_embedded_cover(f):

    tags = tagreader.get_tags(f)
    if ("PICTURE" in tags):
        return _load_apic(tags["PICTURE"])
    else:
        return None


def _load_apic(data):

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
    return picdata
    """
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
    """
