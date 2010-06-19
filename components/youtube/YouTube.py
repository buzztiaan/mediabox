from com import msgs
from storage import Device, File
from utils.MiniXML import MiniXML
from utils import logging
from utils import mimetypes
from utils import threads
from utils import urlquote
from ui.dialog import FileDialog
from ui.dialog import InputDialog
from ui.dialog import OptionDialog
from io import Downloader
from io import FileDownloader
from io import FileServer
from mediabox import values
import platforms
import formats
import config
from theme import theme

import gobject
import gtk
import urllib
import os
import shutil


_YT = "http://www.youtube.com"

_VIDEO_SEARCH = "http://gdata.youtube.com/feeds/api/videos/" \
                "?start-index=%d&max-results=%d&vq=%s"
_VIDEO_WATCH = _YT + "/watch?v=%s"
_VIDEO_FLV = _YT + "/get_video?video_id=%s"
_STD_FEEDS = "http://gdata.youtube.com/feeds/standardfeeds/" \
             "%s?start-index=%d&max-results=%d"

_XMLNS_ATOM = "http://www.w3.org/2005/Atom"
_XMLNS_MRSS = "http://search.yahoo.com/mrss/"
_XMLNS_OPENSEARCH = "http://a9.com/-/spec/opensearchrss/1.0/"
_XMLNS_GOOGLE = "http://schemas.google.com/g/2005"
_XMLNS_YT = "http://gdata.youtube.com/schemas/2007"
_XMLNS_APP = "http://purl.org/atom/app#"

_REGION_BLOCKED = "region blocked"

_SEARCH_CACHE_DIR = os.path.join(values.USER_DIR, "youtube/search-cache")
_VIDEO_FOLDER = "Saved Videos"

_PAGE_SIZE = 25


_STAR_CHAR = u"\u2606"
_STAR2_CHAR = u"\u2605"

_N8x0_FORMAT_WHITELIST = [5, 6, 13]
_N900_FORMAT_WHITELIST = [5, 6, 13, 17, 18]

        

class YouTube(Device):
    """
    StorageDevice for accessing YouTube.
    """
    
    TYPE = Device.TYPE_VIDEO
    CATEGORY = Device.CATEGORY_WAN
    

    def __init__(self):
    
        try:
            os.makedirs(_SEARCH_CACHE_DIR)
        except:
            pass
            
        self.__fileserver = FileServer()
        self.__flv_downloader = None
        
        self.__items = []
        self.__current_folder = None
        
        Device.__init__(self)



    def __get_flv(self, ident):

        data = urllib.urlopen(_VIDEO_WATCH % ident).read()
        # normalize
        data = "".join(data.split())
        
        t = self.__extract_t(data)
        formats = self.__find_formats(data)
        fullid = "%s&t=%s" % (ident, t)
        return (_VIDEO_FLV % fullid, formats)
        

    def __extract_t(self, html):
    
        #open("/tmp/yt.html", "w").write(html)
    
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
        
        
    def __find_formats(self, html):
    
        pos = html.find("\",\"fmt_map\":\"")
        if (pos != -1):
            pos2 = html.find("\"", pos + 13)
            fmt_map = urllib.unquote(html[pos + 13:pos2])
            
            print "Formats:", [ part.split("/")[0] for part in fmt_map.split(",") ]
            return [ int(part.split("/")[0]) for part in fmt_map.split(",") ]

        return []
      
        
    def get_prefix(self):
    
        return "youtube://"
        
        
    def get_name(self):
    
        return "YouTube"
        
        
    def get_file(self, path):

        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        f = None
        if (path == "/"):
            f = File(self)
            f.path = "/"
            f.name = "YouTube"
            f.mimetype = f.DIRECTORY
            f.resource = ""
            f.info = "Browse and download videos from YouTube"
            f.icon = theme.youtube_folder.get_path()

        elif (path.startswith("/search")):
            nil, name, category, query, idx = File.unpack_path(path)
            f = File(self)
            f.name = name
            f.mimetype = f.DIRECTORY
            f.path = path
            f.resource = ""

        elif (path.startswith("/videos")):
            f = self.__make_video(path)
        
        return f


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
        

    def __ls_menu(self, cb, *args):
    
        for name, category in [("Search", "video"),
                               ("Featured", "recently_featured"),
                               ("Most Viewed", "most_viewed"),
                               ("Top Rated", "top_rated")]:            
            item = File(self)
            query = ""
            idx = 0
            item.path = File.pack_path("/search", name, category, query, idx)
            item.resource = item.path
            item.name = name
            item.mimetype = File.DIRECTORY
            
            cb(item, *args)
        #end for

        cb(None, *args)


    def __on_receive_xml(self, data, amount, total, xml, category, query, is_toc, cb, *args):
    
        if (not data):
            # finished loading
            #self.__cache_search_result(url, xml[0])
            if (is_toc):
                self.__parse_toc_xml(xml[0], category, query, cb, *args)
            else:
                self.__parse_page_xml(xml[0], cb, *args)
        else:
            xml[0] += data
            


    def __parse_toc_xml(self, xml, category, query, cb, *args):

        def on_receive_node(node):
            if (node.get_name() == "{%s}totalResults" % _XMLNS_OPENSEARCH):
                # read total number of hits
                total_results = int(node.get_pcdata())
                
                # set a sane limit (YouTube cannot handle more anyway)
                total_results = min(total_results, 40 * _PAGE_SIZE)
                
                page = 1
                for n in range(1, total_results, _PAGE_SIZE):
                    f = File(self)
                    f.name = "Page %d" % page
                    f.path = File.pack_path("/search", f.name, category, query, n)
                    f.mimetype = f.DIRECTORY
                    f.info = "Results %d - %d" % (n, min(total_results, n + _PAGE_SIZE - 1))
                    cb(f, *args)
                    page += 1
                #end for
                
                cb(None, *args)
                
            return True
    
        MiniXML(xml, callback = on_receive_node)
    
    
    def __parse_page_xml(self, xml, cb, *args):
    
        def on_receive_node(node):
            if (node.get_name() == "{%s}entry" % _XMLNS_ATOM):
                f = self.__make_video_from_node(node)
                cb(f, *args)

            elif (node.get_name() == "{%s}feed" % _XMLNS_ATOM):
                # finished parsing
                cb (None, *args)
            
            return True
            
        #open("/tmp/youtube.xml", "w").write(xml)
        MiniXML(xml, callback = on_receive_node)


    def __make_video_from_node(self, node):
        """
        Parses the given entry node and returns a file object.
        """
        
        # get ID
        s = node.get_pcdata("{%s}id" % _XMLNS_ATOM)
        video_id = s[s.rfind("/") + 1:]

        # get title and content 
        title = node.get_pcdata("{%s}title" % _XMLNS_ATOM)
        content = node.get_pcdata("{%s}content" % _XMLNS_ATOM)

        # get authors
        author_node = node.get_child("{%s}author" % _XMLNS_ATOM)
        authors = [ c.get_pcdata() for c in author_node.get_children()
                    if c.get_name() == "{%s}name" % _XMLNS_ATOM ]
        authors = ", ".join(authors)

        # check for region restriction
        app_control = node.get_child("{%s}control" % _XMLNS_APP)
        if (app_control):
            yt_state = app_control.get_child("{%s}state" % _XMLNS_YT)
            reason_code = ""
            if (yt_state):
                reason_code = yt_state.get_attr("{%s}reasonCode" % _XMLNS_ATOM)
            if (reason_code == "requesterRegion"):
                region_blocked = True
                video_id = _REGION_BLOCKED
        #end if

        group_node = node.get_child("{%s}group" % _XMLNS_MRSS)
        
        # get thumbnail
        thumbnail_nodes = [ c for c in group_node.get_children()
                            if c.get_name() == "{%s}thumbnail" % _XMLNS_MRSS ]
        if (thumbnail_nodes):
            thumbnail_url = thumbnail_nodes[0].get_attr("{%s}url" % _XMLNS_ATOM)
        else:
            thumbnail_url = ""
            
        # get category
        category_node = group_node.get_child("{%s}category" % _XMLNS_MRSS)
        if (category_node):
            category = category_node.get_attr("{%s}label" % _XMLNS_ATOM)
        else:
            category = ""

        # get player URL
        player_node = group_node.get_child("{%s}player" % _XMLNS_MRSS)
        if (player_node):
            player_url = player_node.get_attr("{%s}url" % _XMLNS_ATOM)
        else:
            player_url = _VIDEO_WATCH + os.path.basename(entry.video_id)

        # get duration
        duration_node = group_node.get_child("{%s}duration" % _XMLNS_YT)
        if (duration_node):
            duration = int(duration_node.get_attr("{%s}seconds" % _XMLNS_ATOM))
        else:
            duration = 0
            
        # get rating
        rating_node = node.get_child("{%s}rating" % _XMLNS_GOOGLE)
        if (rating_node):
            rating = self.__parse_rating(rating_node)
        else:
            rating = "unrated"
        
        # get view count
        statistics_node = node.get_child("{%s}statistics" % _XMLNS_YT)
        if (statistics_node):
            view_count = int(statistics_node.get_attr("{%s}viewCount" % _XMLNS_ATOM))
        else:
            view_count = 0

        secs = duration % 60
        duration /= 60
        mins = duration

        info = "by %s\n" \
               "Duration: %d:%02d\tViews: %d\t" \
               "Rating: %s" \
               % (authors,
                  mins, secs,
                  view_count,
                  rating)

        path = File.pack_path("/videos", title, info, video_id, thumbnail_url)
        
        return self.__make_video(path)
        
        
    def __make_video(self, path):
        """
        Creates a video file object from the given path.
        """
    
        prefix, title, info, video_id, thumbnail_url = File.unpack_path(path)
        
        f = File(self)
        f.name = title
        f.resource = video_id
        f.path = path
        f.mimetype = "video/x-flash-video"

        if (video_id == _REGION_BLOCKED):
           f.info = "This video cannot be viewed in your country."
           f.icon = theme.youtube_restricted.get_path()
        else:
            f.info = info
            f.thumbnailer = "youtube.YouTubeThumbnailer"
            f.thumbnailer_param = thumbnail_url

        return f
        

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

        out = "%0.1f stars" % (rating)
        #out = _STAR2_CHAR * rating
        #out += _STAR_CHAR * (max_rating - rating)
        
        return out


    def __video_search(self, cb, args, query, start_index):

        start_index = int(start_index)

        if (not query):
            # present search dialog
            dlg = InputDialog("Search", label_ok = "Search")
            dlg.add_input("Keywords:", "")
            resp = dlg.run()
            values = dlg.get_values()

            if (resp == dlg.RETURN_OK and values):
                query = urllib.quote_plus(values[0])
            else:
                cb(None, *args)
                return
                
            url = _VIDEO_SEARCH % (1, 1, query)
            #print "URL", url
            Downloader(url, self.__on_receive_xml, [""], "video", query, True, cb, *args)
            
        else:
            url = _VIDEO_SEARCH % (start_index, _PAGE_SIZE, query)
            #print "URL", url
            Downloader(url, self.__on_receive_xml, [""], "video", query, False, cb, *args)
        #end if

       
    def __category_search(self, category, cb, args, start_index):

        start_index = int(start_index)
        
        #print category, start_index
        if (start_index == 0):
            url = _STD_FEEDS % (category, 1, 1)
            Downloader(url, self.__on_receive_xml, [""], category, "", True, cb, *args)
        else:
            url = _STD_FEEDS % (category, start_index, _PAGE_SIZE)
            Downloader(url, self.__on_receive_xml, [""], category, "", False, cb, *args)


    def __ls_search(self, path, cb, *args):

        prefix, name, category, query, idx = File.unpack_path(path)
        #print path
        #print prefix, name, category, query, idx
        if (category == "video"):
            self.__video_search(cb, args, query, idx)
        else:
            self.__category_search(category, cb, args, idx)


    """
    def __ls_local_videos(self, cb, *args):
    
        videos = []
        for path in [os.path.join(os.path.expanduser("~"), _VIDEO_FOLDER),
                     os.path.join("/media/mmc1", _VIDEO_FOLDER),
                     os.path.join("/media/mmc2", _VIDEO_FOLDER)]:
            if (os.path.exists(path) and os.path.isdir(path)):
                for filename in os.listdir(path):
                    if (os.path.splitext(filename.lower())[1] in formats.get_extensions()):
                        videos.append(os.path.join(path, filename))
                #end for
            #end if
        #end for
        
        videos.sort()
        self.__items = []
        for video in videos:
            f = File(self)
            f.path = "/local" + video
            f.mimetype = "video/x-flash-video"
            f.resource = video
            f.name = urlquote.unquote(os.path.basename(video))
            #f.info = "%s\nby %s" % (rating, authors)
            #f.thumbnail = thumbnail
            
            cb(f, *args)
            self.__items.append(f)
        #end for
        cb(None, *args)
    """ 

 
    def get_contents(self, folder, begin_at, end_at, cb, *args):

        if (begin_at > 0):
            cb(None, *args)
            return

        path = folder.path
        if (self.__flv_downloader):
            self.__flv_downloader.cancel()
   
        self.__current_folder = folder
        if (path == "/"):
            self.__ls_menu(cb, *args)

        elif (path.startswith("/search")):
            self.__ls_search(path, cb, *args)
            
        #elif (path.startswith("/local")):
        #    self.__ls_local_videos(cb, *args)
           
           
    def __get_video(self, f):
        """
        Returns the video URL.
        """

        if (f.resource == _REGION_BLOCKED):
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              "This video is not available in your country.")
            return ("", "")
        
        try:
            flv, fmts = self.__get_flv(f.resource)
        except:
            logging.error("could not retrieve video\n%s", logging.stacktrace())
            return ""

        # filter out incompatible formats
        if (platforms.MAEMO5):
            fmts = [ fmt for fmt in fmts if fmt in _N900_FORMAT_WHITELIST ]
        elif (platforms.MAEMO4):
            fmts = [ fmt for fmt in fmts if fmt in _N8x0_FORMAT_WHITELIST ]
            
        # retrieve high-quality version, if desired
        if (len(fmts) > 1):
            qtype = self.__ask_for_quality(fmts)
        else:
            qtype = 0

        print "Requested Video Quality:", qtype

        #qtype = config.get_quality_type()
        if (qtype in fmts):
            flv = flv + "&fmt=%d" % qtype
            ext = "." + formats.get_container(qtype)
        else:
            ext = ".flv"
            
        logging.info("found FLV: %s", flv)

        return flv + "&ext=" + ext


    def get_resource(self, f):

        #"""    
        def on_dload(d, a, t):
            if (d):
                self.emit_message(msgs.MEDIA_EV_DOWNLOAD_PROGRESS, f, a, t)
                #print "%d / %d         " % (a, t)
                #print gobject.main_depth()
                #if (gobject.main_depth() < 3): 
                #gtk.main_iteration(False)
                
            else:
                self.emit_message(msgs.MEDIA_EV_DOWNLOAD_PROGRESS, f, a, t)
            #end if
        #"""

        url = self.__get_video(f)
        #return url

        #"""
        if (self.__flv_downloader):
            self.__flv_downloader.cancel()

        cache_folder = config.get_cache_folder()
        flv_path = os.path.join(cache_folder, ".tube.flv")

        self.__flv_downloader = FileDownloader(url, flv_path, on_dload)
        
        # we don't give the downloaded file directly to the player because
        # if we did so, the player would fall off the video if it reached
        # the end of file before it was downloaded completely.
        # instead we serve it on a webserver to make the player wait for
        # more if the download rate is too low
        self.__fileserver.allow(flv_path, "/" + f.resource + ".flv")
        
        return self.__fileserver.get_location() + "/" + f.resource + ".flv"
        #"""


    def __ask_for_quality(self, fmts):

        dlg = OptionDialog("Choose Quality Version")
        for fmt in fmts:
            dlg.add_option(None, formats.get_description(fmt))
        resp = dlg.run()

        if (dlg.get_choice() != -1):
            return fmts[dlg.get_choice()]
        else:
            return 0


    def __on_download(self, folder, f):

        url = self.__get_video(f)
        if (not url):
            return
            
        dlg = FileDialog(FileDialog.TYPE_SAVE, "Save Video")
        name = File.make_safe_name(f.name)
        ext = mimetypes.mimetype_to_ext(f.mimetype)
        dlg.set_filename(name + ext)
        dlg.run()
        
        destination = dlg.get_filename()
        if (destination):
            self.call_service(msgs.DOWNLOADER_SVC_GET, url,
                              destination)


    def get_file_actions(self, folder, f):

        actions = Device.get_file_actions(self, folder, f)
        if (f.mimetype != f.DIRECTORY):
            actions.append((None, "Download", self.__on_download))

        return actions


    def __make_filename(self, name, ext):
        """
        Creates a (hopefully) valid filename from the given name.
        """
        
        replace_map = [("/", "-"),
                       ("?", ""),
                       ("\\", "-"),
                       (":", "-")]
                       
        for a, b in replace_map:
            name = name.replace(a, b)

        return name + ext

