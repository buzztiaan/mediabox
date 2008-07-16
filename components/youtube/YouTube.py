from storage import Device, File
from utils.MiniXML import MiniXML
from utils import logging
from ui.Dialog import Dialog
from io.Downloader import Downloader
from io.FileDownloader import FileDownloader
import theme

import gobject
import urllib


_VIDEO_SEARCH = "http://gdata.youtube.com/feeds/api/videos/?vq=%s"
_VIDEO_WATCH = "http://www.youtube.com/watch?v=%s"
_VIDEO_FLV = "http://www.youtube.com/get_video?video_id=%s"

_XMLNS_ATOM = "http://www.w3.org/2005/Atom"
_XMLNS_MRSS = "http://search.yahoo.com/mrss/"



class YouTube(Device):
    """
    StorageDevice for accessing YouTube.
    """

    def __init__(self):
    
        pass


    def __get_flv(self, ident):

        data = urllib.urlopen(_VIDEO_WATCH % ident).read()
        t = self.__extract_t(data)
        fullid = "%s&t=%s" % (ident, t)
        return _VIDEO_FLV % fullid
        

    def __extract_t(self, html):
    
        # normalize
        html = "".join(html.split())
        
        pos = html.find("\",\"t\":\"")
        if (pos != -1):
            pos2 = html.find("\"", pos + 7)
            t = html[pos + 7:pos2]
            print "T", t
            return t
            
        pos = html.find("&t=")
        if (pos != -1):
            pos2 = html.find("&", pos + 3)
            t = html[pos + 3:pos2]
            print "T", t
            return t
        
        return ""        
        
        
    def get_prefix(self):
    
        return "youtube://"
        
        
    def get_name(self):
    
        return "YouTube"
        
        
    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = ""
        
        return f
        
        
    def get_file(self, path):
    
        pass
        
        
    def __send_async(self, items, cb, *args):
    
        if (not items):
            return False
            
        else:
            item = items.pop(0)
            return cb(item, *args)
        

    def __ls_menu(self):
    
        items = []
        for name, path, mimetype, emblem in \
          [("Search", "/search", File.DIRECTORY, None),
           ("Featured", "/featured", File.DIRECTORY, None),
           ("Most viewed", "/mostviewed", File.DIRECTORY, None),
           ("Top rated", "/toprated", File.DIRECTORY, None),
           ("Categories", "/categories", File.DIRECTORY, None)]:
            item = File(self)
            item.path = path
            item.resource = path
            item.name = name
            item.mimetype = mimetype
            item.emblem = emblem
            items.append(item)
        #end for
        
        return items


    def __ls_search(self, cb, *args):

        def on_receive_xml(data, amount, total, xml):
            print "XML", data, amount, total
            xml[0] += data
            if (data):
                pass
            else:
                MiniXML(xml[0], callback = on_receive_item)
            #end if
        
        def on_receive_item(node):
            if (node.get_name() == "{%s}entry" % _XMLNS_ATOM):
                print "got node", node
                s = node.get_pcdata("{%s}id" % _XMLNS_ATOM)
                ident = s[s.rfind("/") + 1:]        
            
                title = node.get_pcdata("{%s}title" % _XMLNS_ATOM)
                content = node.get_pcdata("{%s}content" % _XMLNS_ATOM)

                author_node = node.get_child("{%s}author" % _XMLNS_ATOM)
                authors = [ c.get_pcdata() for c in author_node.get_children()
                            if c.get_name() == "{%s}name" % _XMLNS_ATOM ]
                authors = ", ".join(authors)
            
                group_node = node.get_child("{%s}group" % _XMLNS_MRSS)
                thumbnail_nodes = [ c for c in group_node.get_children()
                                    if c.get_name() == "{%s}thumbnail" % _XMLNS_MRSS ]
                thumbnail = thumbnail_nodes[0].get_attr("{%s}url" % _XMLNS_ATOM)
                
                player_url = group_node.get_child("{%s}player" % _XMLNS_MRSS) \
                                       .get_attr("{%s}url" % _XMLNS_ATOM)
                                       
                f = File(self)
                f.path = ident
                f.mimetype = "video/x-flash-video"
                f.resource = ident
                f.name = title
                f.info = content
                f.thumbnail = thumbnail
                
                try:
                    return cb(f, *args)
                except:
                    import traceback; traceback.print_exc()
                    return False
            else:
                return True            


        # present search dialog            
        dlg = Dialog()
        dlg.add_entry("Keywords:", "")
        # this has no effect on maemo, unless window positioning has been
        # enabled on the window manager, in which case this is required to
        # have the window appear on screen (easy-chroot-debian is known to
        # switch on window positioning)
        dlg.move(0, 0)
        values = dlg.wait_for_values()

        if (values):
            query = values[0]
            Downloader(_VIDEO_SEARCH % query, on_receive_xml, [""])

        
    def ls(self, path):
        
        if (path == "/"):
            return self.__ls_menu()
            
        elif (path == "/search"):
            return self.__ls_search()

        else:
            return []


    def ls_async(self, path, cb, *args):
    
        if (path == "/"):
            gobject.timeout_add(0, self.__send_async, self.__ls_menu(),
                                cb, *args)
        elif (path == "/search"):
            self.__ls_search(cb, *args)
            
            
    def get_resource(self, resource):
    
        def f(d, a, t):
            print "%d / %d" % (a, t)
        
        flv = self.__get_flv(resource)
        FileDownloader(flv, "/tmp/tube.flv", f)    
        
        import time
        time.sleep(15)
        return "/tmp/tube.flv"

