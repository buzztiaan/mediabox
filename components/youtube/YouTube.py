from storage import Device, File
from utils.MiniXML import MiniXML
from utils import logging
from ui.Dialog import Dialog
from io import Downloader
from io import FileDownloader
from io import FileServer
from mediabox import values
import config
import theme

import gobject
import gtk
import urllib
import os


_VIDEO_SEARCH = "http://gdata.youtube.com/feeds/api/videos/" \
                "?start-index=%d&max-results=%d&vq=%s"
_VIDEO_WATCH = "http://www.youtube.com/watch?v=%s"
_VIDEO_FLV = "http://www.youtube.com/get_video?video_id=%s"
_STD_FEEDS = "http://gdata.youtube.com/feeds/standardfeeds/" \
             "%s?start-index=%d&max-results=%d"

_XMLNS_ATOM = "http://www.w3.org/2005/Atom"
_XMLNS_MRSS = "http://search.yahoo.com/mrss/"
_XMLNS_OPENSEARCH = "http://a9.com/-/spec/opensearchrss/1.0/"

_SEARCH_CACHE_DIR = os.path.join(values.USER_DIR, "youtube/search-cache")

_PAGE_SIZE = 25



class _SearchContext(object):

    def __init__(self):
        
        self.url = ""
        self.previous_path = ""
        self.next_path = ""
        self.start_index = 1
        self.page_size = _PAGE_SIZE
                

class YouTube(Device):
    """
    StorageDevice for accessing YouTube.
    """
    
    CATEGORY = Device.CATEGORY_WAN
    

    def __init__(self):
    
        try:
            os.makedirs(_SEARCH_CACHE_DIR)
        except:
            pass
            
        self.__fileserver = FileServer()
        self.__flv_downloader = None



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
        
        
    def get_icon(self):
    
        return theme.youtube_device
        
        
    def get_prefix(self):
    
        return "youtube://"
        
        
    def get_name(self):
    
        return "YouTube"
        
        
    def get_root(self):
    
        f = File(self)
        f.source_icon = self.get_icon()
        f.path = "/"
        f.name = "YouTube"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        
        return f
        
        
    def get_file(self, path):
    
        f = File(self)
        f.source_icon = self.get_icon()
        f.path = path
        f.mimetype = "video/x-flash-video"
        f.source_icon = self.get_icon()
        
        return f
        
        
    def __send_async(self, items, cb, *args):
    
        if (not items):
            return False
            
        else:
            item = items.pop(0)
            return cb(item, *args)
        
        
    def __parse_search_path(self, path):
    
        parts = path.split("/")
        category_parts = parts[2].split(",")
        category = category_parts[0]
        params = category_parts[1:]
        
        return (category, params)


    def __get_cached_search(self, url):
          
        return None
        
        name = urllib.quote(url, "") + ".xml"
        path = os.path.join(_SEARCH_CACHE_DIR, name.lower())
        
        print "looking for", path
        
        if (os.path.exists(path)):
            return open(path).read()
        else:
            return None
            
            
            
    def __cache_search_result(self, url, xml):
   
        name = urllib.quote(url, "") + ".xml"
        path = os.path.join(_SEARCH_CACHE_DIR, name.lower())

        try:
            open(path, "w").write(xml)
        except:
            pass
            
        

    def __ls_menu(self):
    
        items = []
        for name, path, mimetype, emblem in \
          [("Search", "/search/video,,1", File.DIRECTORY, None),
           ("Featured", "/search/recently_featured,1", File.DIRECTORY, None),
           ("Most viewed", "/search/most_viewed,1", File.DIRECTORY, None),
           ("Top rated", "/search/top_rated,1", File.DIRECTORY, None),
           ("Categories", "/categories", File.DIRECTORY, None)]:
            item = File(self)
            item.source_icon = self.get_icon()
            item.path = path
            item.resource = path
            item.name = name
            item.mimetype = mimetype
            item.emblem = emblem
            items.append(item)
        #end for

        items.append(None)        
        return items



    def __on_receive_xml(self, data, amount, total, ctx, xml, cb, *args):
    
        xml[0] += data
        if (not data):
            # finished loading
            self.__cache_search_result(ctx.url, xml[0])
            self.__parse_xml(xml[0], ctx, cb, *args)


    def __parse_xml(self, xml, ctx, cb, *args):

        def on_receive_item(node):
            if (node.get_name() == "{%s}totalResults" % _XMLNS_OPENSEARCH):
                # read total number of hits
                total_results = int(node.get_pcdata())

                if (ctx.start_index + _PAGE_SIZE < total_results):
                    a = ctx.start_index + _PAGE_SIZE
                    b = min(total_results, a + _PAGE_SIZE - 1)
                    
                    f = File(self)
                    f.source_icon = self.get_icon()
                    f.path = ctx.next_path
                    f.mimetype = f.DIRECTORY
                    f.name = "Next Results"
                    f.info = "%d - %d of %d" % (a, b, total_results)
                    
                    return cb(f, *args)

                else:
                    return True
                #end if      

        
            elif (node.get_name() == "{%s}entry" % _XMLNS_ATOM):
                #print "got node", node

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
                f.source_icon = self.get_icon()
                f.path = ident
                f.mimetype = "video/x-flash-video"
                f.resource = ident
                f.name = title
                f.info = "by %s" % authors
                f.thumbnail = thumbnail
                f.source_icon = self.get_icon()
                
                #while (gtk.events_pending()): gtk.main_iteration()
                
                return cb(f, *args)

            elif (node.get_name() == "{%s}feed" % _XMLNS_ATOM):
                # finished parsing
                cb (None, *args)

            else:
                return True            


        MiniXML(xml, callback = on_receive_item)



    def __video_search(self, cb, args, query, start_index):
        
        if (not query):
            # present search dialog            
            dlg = Dialog()
            dlg.add_entry("Keywords:", "")
            values = dlg.wait_for_values()

            if (values):
                query = urllib.quote_plus(values[0])
            else:
                return            
        #end if

        start_index = int(start_index)
        
        ctx = _SearchContext()
        if (start_index > 1):
            ctx.previous_path = "/search/video,%s,%d" \
                                % (query, start_index - _PAGE_SIZE)
        ctx.next_path = "/search/video,%s,%d" % (query, start_index + _PAGE_SIZE)
        ctx.start_index = start_index
        ctx.url = _VIDEO_SEARCH % (start_index, _PAGE_SIZE, query)

        xml = self.__get_cached_search(ctx.url)
        if (xml):
            self.__parse_xml(xml, ctx, cb, *args)
        else:
            Downloader(ctx.url, self.__on_receive_xml, ctx, [""], cb, *args)


    def __generic_search(self, name, cb, args, start_index):

        start_index = int(start_index)
        
        ctx = _SearchContext()
        if (start_index > 1):
            ctx.previous_path = "/search/%s,%d" \
                                % (name, start_index - _PAGE_SIZE)
        ctx.next_path = "/search/%s,%d" % (name, start_index + _PAGE_SIZE)
        ctx.start_index = start_index
        ctx.url = _STD_FEEDS % (name, start_index, _PAGE_SIZE)

        xml = self.__get_cached_search(ctx.url)
        if (xml):
            self.__parse_xml(xml, ctx, cb, *args)
        else:
            Downloader(ctx.url, self.__on_receive_xml, ctx, [""], cb, *args)
    

    def __ls_search(self, path, cb, *args):

        category, params = self.__parse_search_path(path)
        if (category == "video"):
            self.__video_search(cb, args, *params)
        elif (category == "recently_featured"):
            self.__generic_search("recently_featured", cb, args, *params)
        elif (category == "most_viewed"):
            self.__generic_search("most_viewed", cb, args, *params)
        elif (category == "top_rated"):
            self.__generic_search("top_rated", cb, args, *params)


        

    def ls_async(self, path, cb, *args):
    
        if (path == "/"):
            gobject.timeout_add(0, self.__send_async, self.__ls_menu(),
                                cb, *args)

        elif (path.startswith("/search")):
            self.__ls_search(path, cb, *args)
            
            
    def get_resource(self, resource):
    
        def f(d, a, t):
            print "%d / %d         " % (a, t)
            print gobject.main_depth()
            if (gobject.main_depth() < 3): gtk.main_iteration(False)
            
        flv = self.__get_flv(resource)

        if (self.__flv_downloader):
            self.__flv_downloader.cancel()
            
        cache_folder = config.get_cache_folder()
        flv_path = os.path.join(cache_folder, ".tube.flv")
        self.__flv_downloader = FileDownloader(flv, flv_path, f)
        
        # we don't give the downloaded file directly to the player because
        # if we did so, the player would fall off the video if it reached
        # the end of file before it was downloaded completely.
        # instead we serve it on a webserver to make the player wait for
        # more if the download rate is too low
        self.__fileserver.allow(flv_path, "/" + resource + ".flv")
        
        return self.__fileserver.get_location() + "/" + resource + ".flv"

