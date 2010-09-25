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


"""
Relevance: youtube.com/results?search_type=videos&search_query=n900&suggested_categories=28&uni=3
Upload date: youtube.com/results?search_type=videos&search_query=n900&search_sort=video_date_uploaded&suggested_categories=28&uni=3
View count: youtube.com/results?search_type=videos&search_query=n900&search_sort=video_view_count&suggested_categories=28&uni=3
Rating: youtube.com/results?search_type=videos&search_query=n900&search_sort=video_avg_rating&suggested_categories=28&uni=3 
"""

_YT = "http://www.youtube.com"

_VIDEO_SEARCH = "http://gdata.youtube.com/feeds/api/videos/" \
                "?start-index=%d&max-results=%d&vq=%s"

if (platforms.MAEMO5):
    _VIDEO_WATCH = _YT + "/watch?v=%s&fmt=18"
else:
    _VIDEO_WATCH = _YT + "/watch?v=%s"

_VIDEO_FLV = _YT + "/get_video?video_id=%s"
_STD_FEEDS = "http://gdata.youtube.com/feeds/standardfeeds/"

_XMLNS_ATOM = "http://www.w3.org/2005/Atom"
_XMLNS_MRSS = "http://search.yahoo.com/mrss/"
_XMLNS_OPENSEARCH = "http://a9.com/-/spec/opensearchrss/1.0/"
_XMLNS_GOOGLE = "http://schemas.google.com/g/2005"
_XMLNS_YT = "http://gdata.youtube.com/schemas/2007"
_XMLNS_APP = "http://purl.org/atom/app#"

_VIDEOS_API = "http://gdata.youtube.com/feeds/api/videos"
_SEARCH_PARAMS = "?start-index=%d&max-results=%d"
_SEARCH_PARAMS2 = "&start-index=%d&max-results=%d"
_CATEGORIES = {
    "recently_featured": _STD_FEEDS + "recently_featured" + _SEARCH_PARAMS,
    "most_viewed":       _STD_FEEDS + "most_viewed" + _SEARCH_PARAMS,
    "most_popular":      _STD_FEEDS + "most_popular" + _SEARCH_PARAMS,
    "top_rated":         _STD_FEEDS + "top_rated?time=today" + _SEARCH_PARAMS2,
    "watch_on_mobile":   _STD_FEEDS + "watch_on_mobile" + _SEARCH_PARAMS,
    "music":             _VIDEOS_API + "?category=Music&orderby=published" + _SEARCH_PARAMS2,
    "movie":             _VIDEOS_API + "?category=Movies&orderby=published" + _SEARCH_PARAMS2,
    "news":              _VIDEOS_API + "?category=News&orderby=published" + _SEARCH_PARAMS2
}
_ICONS = {
    "Search": theme.youtube_search,
    "Today's Top Rated": theme.mb_folder_mydocs,
    "Music": theme.mb_folder_audioclips,
    "Movies": theme.mb_folder_videoclips
}

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
        """
        Returns a dictionary of format IDs and video URLs for a given video
        identified by its ID.
        """

        data = urllib.urlopen(_VIDEO_WATCH % ident).read()
        # normalize
        data = "".join(data.split())
        
        #t = self.__extract_t(data)
        #t = t.replace("%3D", "=")
        #print "found T:", t
        #fullid = "%s&t=%s" % (ident, t)
        #return (_VIDEO_FLV % fullid, formats)
        formats = self.__find_formats(data)
        return formats
        

    """
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
    """
        
    def __find_formats(self, html):
        """
        Returns a dictionary with the available formats and video URLs.
        """
    
        formats = {}
        pos = html.find("\",\"fmt_url_map\":\"")
        if (pos != -1):
            pos2 = html.find("\"", pos + 17)
            fmt_map = urllib.unquote(html[pos + 17:pos2]) + ","
            #print fmt_map

            parts = fmt_map.split("|")
            key = parts[0]
            for p in parts[1:]:
                idx = p.rfind(",")
                value = p[:idx].replace("\\/", "/")
                formats[int(key)] = value
                key = p[idx + 1:]
            #end for
        #end if

        print "Formats:", formats
        return formats
      
        
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
            if (name in _ICONS):
                f.icon = _ICONS[name].get_path()

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
    
        for name, category in [
            ("Search", "video"),
            ("Recently Featured", "recently_featured"),
            ("Today's Top Rated", "top_rated"),
            ("Most Viewed", "most_viewed"),
            ("Most Popular", "most_popular"),
            ("Music", "music"),
            ("Movies", "movie"),
            ("News", "news"),
            ("For Mobile Phones", "watch_on_mobile")
        ]:
            item = File(self)
            query = ""
            idx = 0
            item.path = File.pack_path("/search", name, category, query, idx)
            item.resource = item.path
            item.name = name
            item.mimetype = File.DIRECTORY
            item.folder_flags = File.ITEMS_UNSORTED
            if (name in _ICONS):
                item.icon = _ICONS[name].get_path()
            
            cb(item, *args)
        #end for

        cb(None, *args)


    def __on_receive_xml(self, data, amount, total, xml, category, query, is_toc, cb, *args):
    
        if (data == None):
            # error
            logging.error("error downloading XML data")
            self.__current_folder.message = "content not available"
            cb(None, *args)
            
        elif (not data):
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
                total_results = min(total_results, 20 * _PAGE_SIZE)
                
                page = 1
                for n in range(1, total_results, _PAGE_SIZE):
                    f = File(self)
                    f.name = "Page %d" % page
                    f.path = File.pack_path("/search", f.name, category, query, n)
                    f.mimetype = f.DIRECTORY
                    f.info = "Results %d - %d" % (n, min(total_results, n + _PAGE_SIZE - 1))
                    f.folder_flags = File.ITEMS_UNSORTED
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
               "%d:%02d\t%s\t%s views" \
               % (authors,
                  mins, secs,
                  rating,
                  view_count)

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
            url = _CATEGORIES[category] % (1, 1)
            Downloader(url, self.__on_receive_xml, [""], category, "", True, cb, *args)
        else:
            url = _CATEGORIES[category] % (start_index, _PAGE_SIZE)
            Downloader(url, self.__on_receive_xml, [""], category, "", False, cb, *args)


    def __ls_search(self, path, cb, *args):

        prefix, name, category, query, idx = File.unpack_path(path)
        #print path
        #print prefix, name, category, query, idx
        if (category == "video"):
            self.__video_search(cb, args, query, idx)
        else:
            self.__category_search(category, cb, args, idx)

 
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
            fmts = self.__get_flv(f.resource)
        except:
            logging.error("could not retrieve video\n%s", logging.stacktrace())
            return ""

        #if (not 18 in fmts): fmts.append(18)
        f_ids = fmts.keys()
        f_ids.sort(formats.comparator)

        # filter out incompatible formats
        if (platforms.MAEMO5):
            f_ids = [ f for f in f_ids if f in _N900_FORMAT_WHITELIST ]
        elif (platforms.MAEMO4):
            f_ids = [ f for f in f_ids if f in _N8x0_FORMAT_WHITELIST ]
            
        # retrieve high-quality version, if desired
        if (len(f_ids) > 1):
            qtype = self.__ask_for_quality(f_ids)
        elif (len(f_ids) == 1):
            qtype = f_ids[0]
        else:
            qtype = 5

        print "Requested Video Quality:", qtype

        flv = fmts[qtype]
        ext = "." + formats.get_container(qtype)
        logging.info("found FLV: %s", flv)
        return flv + "&ext=" + ext
        

    def get_resource(self, f):

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

        url = self.__get_video(f)

        if (self.__flv_downloader):
            self.__flv_downloader.cancel()

        # the mplayer backend on Maemo4 doesn't work well with directly
        # taking an URL from YouTube for some reason
        if (platforms.MAEMO4):
            cache_folder = config.get_cache_folder()
            try:
                if (not os.path.exists(cache_folder)):
                    os.mkdir(cache_folder)
            except:
                import traceback; traceback.print_exc()
                return ""
            flv_path = os.path.join(cache_folder, ".tube.flv")

            self.__flv_downloader = FileDownloader(url, flv_path, on_dload)
        
            # we don't give the downloaded file directly to the player because
            # if we did so, the player would fall off the video if it reached
            # the end of file before it was downloaded completely.
            # instead we serve it on a webserver to make the player wait for
            # more if the download rate is too low
            self.__fileserver.allow(flv_path, "/" + f.resource + ".flv")
        
            url = self.__fileserver.get_location() + "/" + f.resource + ".flv"
        #end if
        
        return url


    def __ask_for_quality(self, fmts):

        # the list of formats comes in sorted already

        quality_mode = config.get_quality()

        if (quality_mode == config.QUALITY_LOW):
            return fmts[0]
            
        elif (quality_mode == config.QUALITY_HIGH):
            return fmts[-1]
            
        else:
            dlg = OptionDialog("Choose Quality Version")
            for fmt in fmts:
                dlg.add_option(None, formats.get_description(fmt))
            resp = dlg.run()

            if (dlg.get_choice() != -1):
                return fmts[dlg.get_choice()]
            else:
                return 5


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

