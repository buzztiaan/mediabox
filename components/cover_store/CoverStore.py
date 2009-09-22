from com import Component, msgs
from mediabox import tagreader
from utils import imageloader

import os


class CoverStore(Component):

    def __init__(self):
    
        Component.__init__(self)
        
        
    def handle_COVERSTORE_SVC_GET_COVER(self, f, cb, *args):
        
        if (f.resource.startswith("/")):
            # it's a local file
            if (f.mimetype.endswith("-folder")):
                # it's a directory
                cover = self.__find_cover_file(f.resource)
                if (cover):
                    imageloader.load(cover, cb, *args)
                else:
                    cb(None, *args)
                    
            else:
                # it's a regular file
                cover = self.__find_cover_of_file(f)
                if (cover):
                    imageloader.load(cover, cb, *args)
                else:
                    embedded = self.__find_embedded_cover(f)
                    if (embedded):
                        imageloader.load_data(embedded, cb, *args)
                    else:
                        cb(None, *args)

                #end if   

        else:
            # it's a remote file
            cb(None, *args)
        
    
        # tell the message bus that we handled this service call
        return 0      
              
        
    def __find_cover_file(self, uri):

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


    def __find_cover_of_file(self, f):

        if (not f.resource.startswith("/")):
            return None
            
        parent = os.path.dirname(f.resource)
        return self.__find_cover_file(parent)



    def __find_embedded_cover(self, f):

        tags = tagreader.get_tags(f)
        if ("PICTURE" in tags):
            return self.__load_apic(tags["PICTURE"])
        else:
            return None


    def __load_apic(self, data):

        idx = data.find("\x00", 1)
        idx = data.find("\x00", idx + 1)
        while (data[idx] == "\x00"): idx += 1
        
        picdata = data[idx:]
        return picdata

