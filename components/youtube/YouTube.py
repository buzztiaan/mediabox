from com import msgs
from storage import Device, File
from utils.MiniXML import MiniXML
from utils import logging
from utils import threads
from utils import urlquote
from ui.Dialog import Dialog
from io import Downloader
from io import FileDownloader
from io import FileServer
from mediabox import values
import config
from theme import theme

import gobject
import gtk
import urllib
import os
import shutil


_VIDEO_SEARCH = "http://gdata.youtube.com/feeds/api/videos/" \
                "?start-index=%d&max-results=%d&vq=%s"
_VIDEO_WATCH = "http://www.youtube.com/watch?v=%s"
_VIDEO_FLV = "http://www.youtube.com/get_video?video_id=%s"
_STD_FEEDS = "http://gdata.youtube.com/feeds/standardfeeds/" \
             "%s?start-index=%d&max-results=%d"

_XMLNS_ATOM = "http://www.w3.org/2005/Atom"
_XMLNS_MRSS = "http://search.yahoo.com/mrss/"
_XMLNS_OPENSEARCH = "http://a9.com/-/spec/opensearchrss/1.0/"
_XMLNS_GOOGLE = "http://schemas.google.com/g/2005"

_SEARCH_CACHE_DIR = os.path.join(values.USER_DIR, "youtube/search-cache")
_VIDEO_FOLDER = "Saved Videos"

_PAGE_SIZE = 25


_STAR_CHAR = u"\u2606"
_STAR2_CHAR = u"\u2605"


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
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self):
    
        try:
            os.makedirs(_SEARCH_CACHE_DIR)
        except:
            pass
            
        self.__fileserver = FileServer()
        self.__flv_downloader = None
        
        self.__keep_video = False
        
        Device.__init__(self)



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
        f.path = "/"
        f.name = "YouTube"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        
        return f
        
        
    def get_file(self, path):
    
        f = File(self)
        f.path = path
        f.mimetype = "video/x-flash-video"
        
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
          [("Saved Videos", "/local", File.DIRECTORY, None),
           ("Search", "/search/video,,1", File.DIRECTORY, None),
           ("Featured", "/search/recently_featured,1", File.DIRECTORY, None),
           ("Most viewed", "/search/most_viewed,1", File.DIRECTORY, None),
           ("Top rated", "/search/top_rated,1", File.DIRECTORY, None)]:
           #("Categories", "/categories", File.DIRECTORY, None)]:
            item = File(self)
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
                
                rating_node = node.get_child("{%s}rating" % _XMLNS_GOOGLE)
                rating = self.__parse_rating(rating_node)
               
                f = File(self)
                f.can_keep = True
                f.path = ident
                f.mimetype = "video/x-flash-video"
                f.resource = ident
                f.name = title
                f.info = "%s\nby %s" % (rating, authors)
                f.thumbnail = thumbnail
                
                #while (gtk.events_pending()): gtk.main_iteration()
                
                return cb(f, *args)

            elif (node.get_name() == "{%s}feed" % _XMLNS_ATOM):
                # finished parsing
                cb (None, *args)

            else:
                return True            


        #open("/tmp/yt.xml", "w").write(xml)
        MiniXML(xml, callback = on_receive_item)


    def __parse_rating(self, node):
        """
        Parses the rating node and returns a string representation.
        """
    
        try:
            rating = float(node.get_attr("{%s}average" % _XMLNS_ATOM))
            #rating = int(rating + 0.5)
            max_rating = int(node.get_attr("{%s}max" % _XMLNS_ATOM))
        except:
            #import traceback; traceback.print_exc()
            #return _STAR_CHAR * 5
            return ""

        out = "rated %0.1f stars" % (rating)
        #out = _STAR2_CHAR * rating
        #out += _STAR_CHAR * (max_rating - rating)
        
        return out


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



    def __ls_local_videos(self, cb, *args):
    
        videos = []
        for path in [os.path.join(os.path.expanduser("~"), _VIDEO_FOLDER),
                     os.path.join("/media/mmc1", _VIDEO_FOLDER),
                     os.path.join("/media/mmc2", _VIDEO_FOLDER)]:
            if (os.path.exists(path) and os.path.isdir(path)):
                for filename in os.listdir(path):
                    if (filename.lower().endswith(".flv")):
                        videos.append(os.path.join(path, filename))
                #end for
            #end if
        #end for
        
        videos.sort()
        for video in videos:
            f = File(self)
            f.path = "/local" + video
            f.mimetype = "video/x-flash-video"
            f.resource = video
            f.name = urlquote.unquote(os.path.basename(video))
            #f.info = "%s\nby %s" % (rating, authors)
            #f.thumbnail = thumbnail
            
            cb(f, *args)
        #end for
        cb(None, *args)
        

    def ls_async(self, path, cb, *args):

        if (self.__flv_downloader):
            self.__flv_downloader.cancel()
    
        if (path == "/"):
            gobject.timeout_add(0, self.__send_async, self.__ls_menu(),
                                cb, *args)

        elif (path.startswith("/search")):
            self.__ls_search(path, cb, *args)
            
        elif (path.startswith("/local")):
            self.__ls_local_videos(cb, *args)
            
            
    def get_resource(self, f):
    
        def on_dload(d, a, t, flv_path, keep_path):
            if (d):
                print "%d / %d         " % (a, t)
                print gobject.main_depth()
                #if (gobject.main_depth() < 3): 
                gtk.main_iteration(False)
                
            else:
                if (self.__keep_video):
                    keep_dir = os.path.dirname(keep_path)
                    if (not os.path.exists(keep_dir)):
                        try:
                            os.makedirs(os.path.dirname(keep_path))
                        except:
                            pass
                    #end if
                    try:
                        os.rename(flv_path, keep_path)
                    except:
                        logging.error("could not save video '%s'\n%s" \
                                      % (keep_path, logging.stacktrace()))
                    # copy thumbnail
                    self.__copy_thumbnail(f, keep_path)
                #end if
            #end if


        if (f.resource.startswith("/")): return f.resource
        
        self.emit_event(msgs.UI_ACT_SHOW_MESSAGE,
                        "Requesting Video",
                        "- %s -" % f.name,
                        theme.youtube_device)
        try:
            flv = self.__get_flv(f.resource)
        except:
            return ""
        self.emit_event(msgs.UI_ACT_HIDE_MESSAGE)

        if (self.__flv_downloader):
            self.__flv_downloader.cancel()
            
        cache_folder = config.get_cache_folder()
        flv_path = os.path.join(cache_folder, ".tube.flv")
        keep_path = os.path.join(cache_folder, _VIDEO_FOLDER,
                                 self.__make_filename(f.name))
        self.__keep_video = False
        self.__flv_downloader = FileDownloader(flv, flv_path, on_dload,
                                               flv_path, keep_path)
        
        # we don't give the downloaded file directly to the player because
        # if we did so, the player would fall off the video if it reached
        # the end of file before it was downloaded completely.
        # instead we serve it on a webserver to make the player wait for
        # more if the download rate is too low
        self.__fileserver.allow(flv_path, "/" + f.resource + ".flv")
        
        return self.__fileserver.get_location() + "/" + f.resource + ".flv"


    def keep(self, f):
        """
        Keeps the current video.
        """
        
        self.__keep_video = True
        self.emit_event(msgs.NOTIFY_SVC_SHOW_INFO,
                        u"video will be saved as\n\xbb%s\xab" \
                        % self.__make_filename(f.name))



    def __make_filename(self, name):
        """
        Creates a (hopefully) valid filename from the given name.
        """
        
        replace_map = [("/", "-"),
                       ("?", ""),
                       ("\\", "-"),
                       (":", "-")]
                       
        for a, b in replace_map:
            name = name.replace(a, b)

        #return urlquote.quote(name, " ") + ".flv"
        return name + ".flv"


    def __copy_thumbnail(self, f, path):
    
        tn, uptodate = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
        f2 = File(self)
        f2.path = "/local" + path
        tn2, uptodate = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f2)

        if (os.path.exists(tn)):
            try:
                shutil.copyfile(tn, tn2)
            except:
                pass
                
