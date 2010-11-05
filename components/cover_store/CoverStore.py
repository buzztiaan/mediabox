from com import Component, msgs
from mediabox import tagreader
from mediabox import imageloader
from theme import theme

import gobject
import os
import threading
import time
from Queue import Queue


class CoverStore(Component):
    """
    Component for retrieving and providing cover art.
    """

    def __init__(self):
    
        self.__queue = Queue()
    
        Component.__init__(self)

        t = threading.Thread(target = self.__cover_thread)
        t.setDaemon(True)
        t.start()

        
    def handle_COVERSTORE_SVC_GET_COVER(self, f, cb, *args):
        
        self.__queue.put((f, cb, args))
        #cb(None, *args)

        # tell the message bus that we handled this service call
        return 0      
        
        
    def __emit(self, cb, cover_file, cover_data, *args):
    
        if (cover_file):
            gobject.timeout_add(0, imageloader.load, cover_file, cb, *args)
        elif (cover_data):
            gobject.timeout_add(0, imageloader.load_data, cover_data, cb, *args)
        else:
            gobject.timeout_add(0, cb, None, *args)
        
        
    def __cover_thread(self):
    
        while (True):
            time.sleep(0.1)
            f, cb, args = self.__queue.get()
        
            if (f.resource.startswith("/") and os.path.exists(f.resource)):
                # it's a local file
                if (f.mimetype.endswith("-folder")):
                    # it's a directory
                    cover_file = self.__find_cover_file(f.resource)
                    self.__emit(cb, cover_file, None, *args)
                    
                else:
                    # it's a regular file
                    cover_file = self.__find_cover_of_file(f)
                    if (cover_file):
                        self.__emit(cb, cover_file, None, *args)
                    else:
                        embedded = self.__find_embedded_cover(f)
                        if (embedded):
                            self.__emit(cb, None, embedded, *args)
                        else:
                            self.__emit(cb, None, None, *args)

                    #end if   

            else:
                # it's a remote file
                self.__emit(cb, None, None, *args)
                
        #end while
    
              
        
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

