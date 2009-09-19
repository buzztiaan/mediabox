from com import msgs
from storage import Device, File
from utils.MiniXML import MiniXML
from utils import logging
from utils import threads
from utils import urlquote
from ui import dialogs
from ui.Dialog import Dialog
from io import Downloader
from io import FileDownloader
from io import FileServer
from mediabox import values
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


class _SearchContext(object):

    def __init__(self):
        
        self.query = ""
        self.url = ""
        self.previous_path = ""
        self.next_path = ""
        self.start_index = 1
        self.page_size = _PAGE_SIZE


class _YTEntry(object):

    def __init__(self):
    
        self.video_id = ""
        self.title = ""
        self.content = ""
        self.authors = ""
        self.category = "uncategorized"
        self.duration = 0
        self.view_count = 0
        self.thumbnail_url = ""
        self.player_url = ""
        self.region_blocked = False
        

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
            fmt_map = html[pos + 13:pos2]
            print "Formats:", [ part.split("/")[0] for part in fmt_map.split(",") ]
            return [ int(part.split("/")[0]) for part in fmt_map.split(",") ]

        return []
        
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
        f.info = "Browse and download videos from YouTube"
        
        return f
        
        
    def get_file(self, path):
    
        f = File(self)
        f.path = path
        f.mimetype = "video/x-flash-video"
        
        return f
        

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
            
        

    def __ls_menu(self, cb, *args):
    
        for name, path, mimetype, emblem in \
          [("Saved Videos", "/local", File.DIRECTORY, None),
           ("Search", "/search/video,,0", File.DIRECTORY, None),
           ("Featured Videos", "/search/recently_featured,0", File.DIRECTORY, None),
           ("Most Viewed Videos", "/search/most_viewed,0", File.DIRECTORY, None),
           ("Top Rated Videos", "/search/top_rated,0", File.DIRECTORY, None)]:
           #("Categories", "/categories", File.DIRECTORY, None)]:
            item = File(self)
            item.path = path
            item.resource = path
            item.name = name
            item.mimetype = mimetype
            if (path != "/local"):
                item.folder_flags = item.ITEMS_DOWNLOADABLE
            else:
                item.folder_flags = item.ITEMS_DELETABLE
            
            cb(item, *args)
        #end for

        cb(None, *args)




    def __on_receive_xml(self, data, amount, total, xml, query, is_toc, cb, *args):
    
        xml[0] += data
        if (not data):
            # finished loading
            #print xml[0]
            #self.__cache_search_result(url, xml[0])
            if (is_toc):
                self.__parse_toc_xml(xml[0], query, cb, *args)
            else:
                self.__parse_page_xml(xml[0], cb, *args)


    def __parse_toc_xml(self, xml, query, cb, *args):

        def on_receive_node(node):
            if (node.get_name() == "{%s}totalResults" % _XMLNS_OPENSEARCH):
                # read total number of hits
                total_results = int(node.get_pcdata())
                
                page = 1
                for n in range(1, total_results, _PAGE_SIZE):
                    f = File(self)
                    f.path = "/search/%s,%d" % (query, n)
                    f.mimetype = f.DIRECTORY
                    f.name = "Page %d" % page
                    f.info = "Results %d - %d" % (n, min(total_results, n + _PAGE_SIZE - 1))
                    f.folder_flags = f.ITEMS_DOWNLOADABLE
                    cb(f, *args)
                    page += 1
                #end for
                
                cb(None, *args)
                
            return True
    
    
        MiniXML(xml, callback = on_receive_node)
    
    
    def __parse_page_xml(self, xml, cb, *args):
    
        def on_receive_node(node):
            if (node.get_name() == "{%s}entry" % _XMLNS_ATOM):
                entry = self.__parse_yt_entry(node)
               
                f = File(self)
                f.path = entry.video_id
                f.mimetype = "video/x-flash-video"
                f.name = "%s" % entry.title
                f.resource = entry.video_id
                duration = entry.duration
                secs = duration % 60
                duration /= 60
                mins = duration
                if (entry.region_blocked):
                    f.info += "This video cannot be viewed in your country."
                    f.icon = theme.youtube_restricted.get_path()
                else:
                    #f.info = "%d:%02d, %s, %d views\nby %s" \
                    f.info = "by %s\n" \
                             "Duration: %d:%02d\tViews: %d\n" \
                             "Rating: %s" \
                             % (entry.authors,
                                mins, secs, entry.view_count,
                                entry.rating)
                    f.thumbnail = entry.thumbnail_url
                
                cb(f, *args)

            elif (node.get_name() == "{%s}feed" % _XMLNS_ATOM):
                # finished parsing
                cb (None, *args)
            
            return True
            
        #open("/tmp/youtube.xml", "w").write(xml)
        MiniXML(xml, callback = on_receive_node)


    def __parse_yt_entry(self, node):
        """
        Parses the given entry node and returns a _YTEntry object.
        """
        
        entry = _YTEntry()
        
        # get ID
        s = node.get_pcdata("{%s}id" % _XMLNS_ATOM)
        entry.video_id = s[s.rfind("/") + 1:]

        # get title and content 
        entry.title = node.get_pcdata("{%s}title" % _XMLNS_ATOM)
        entry.content = node.get_pcdata("{%s}content" % _XMLNS_ATOM)

        # get authors
        author_node = node.get_child("{%s}author" % _XMLNS_ATOM)
        authors = [ c.get_pcdata() for c in author_node.get_children()
                    if c.get_name() == "{%s}name" % _XMLNS_ATOM ]
        entry.authors = ", ".join(authors)

        # check for region restriction
        app_control = node.get_child("{%s}control" % _XMLNS_APP)
        if (app_control):
            yt_state = app_control.get_child("{%s}state" % _XMLNS_YT)
            reason_code = ""
            if (yt_state):
                reason_code = yt_state.get_attr("{%s}reasonCode" % _XMLNS_ATOM)
            if (reason_code == "requesterRegion"):
                entry.region_blocked = True
                entry.video_id = _REGION_BLOCKED
        #end if

        group_node = node.get_child("{%s}group" % _XMLNS_MRSS)
        
        # get thumbnail
        thumbnail_nodes = [ c for c in group_node.get_children()
                            if c.get_name() == "{%s}thumbnail" % _XMLNS_MRSS ]
        if (thumbnail_nodes):
            entry.thumbnail_url = thumbnail_nodes[0].get_attr("{%s}url" % _XMLNS_ATOM)
                    
        # get category
        category_node = group_node.get_child("{%s}category" % _XMLNS_MRSS)
        if (category_node):
            entry.category = category_node.get_attr("{%s}label" % _XMLNS_ATOM)

        # get player URL
        player_node = group_node.get_child("{%s}player" % _XMLNS_MRSS)
        if (player_node):
            entry.player_url = player_node.get_attr("{%s}url" % _XMLNS_ATOM)
        else:
            entry.player_url = _VIDEO_WATCH + os.path.basename(entry.video_id)

        # get duration
        duration_node = group_node.get_child("{%s}duration" % _XMLNS_YT)
        if (duration_node):
            entry.duration = int(duration_node.get_attr("{%s}seconds" % _XMLNS_ATOM))
            
        # get rating
        rating_node = node.get_child("{%s}rating" % _XMLNS_GOOGLE)
        if (rating_node):
            entry.rating = self.__parse_rating(rating_node)
        else:
            entry.rating = "unrated"
        
        # get view count
        statistics_node = node.get_child("{%s}statistics" % _XMLNS_YT)
        if (statistics_node):
            entry.view_count = int(statistics_node.get_attr("{%s}viewCount" % _XMLNS_ATOM))
        
        return entry
        


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
            dlg = Dialog()
            dlg.add_entry("Keywords:", "")
            values = dlg.wait_for_values()

            if (values):
                query = urllib.quote_plus(values[0])
            else:
                cb(None, *args)
                return
                
            url = _VIDEO_SEARCH % (1, 1, query)
            #print "URL", url
            Downloader(url, self.__on_receive_xml, [""], "video," + query, True, cb, *args)
            
        else:
            url = _VIDEO_SEARCH % (start_index, _PAGE_SIZE, query)
            #print "URL", url
            Downloader(url, self.__on_receive_xml, [""], "video," + query, False, cb, *args)
        #end if

       

    def __generic_search(self, name, cb, args, start_index):

        start_index = int(start_index)
        
        if (start_index == 0):
            url = _STD_FEEDS % (name, 1, 1)
            Downloader(url, self.__on_receive_xml, [""], name, True, cb, *args)
        else:
            url = _STD_FEEDS % (name, start_index, _PAGE_SIZE)
            Downloader(url, self.__on_receive_xml, [""], name, False, cb, *args)
        
   

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
                    if (os.path.splitext(filename.lower())[1] in formats.get_extensions()):
                        videos.append(os.path.join(path, filename))
                #end for
            #end if
        #end for
        
        videos.sort()
        self.__items = []
        for video in videos:
            f = File(self)
            f.can_delete = True
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
            
        elif (path.startswith("/local")):
            self.__ls_local_videos(cb, *args)
            
            
    def get_resource(self, f):
    
        def on_dload(d, a, t, flv_path, keep_path):
            if (d):
                self.emit_message(msgs.MEDIA_EV_DOWNLOAD_PROGRESS, f, a, t)
                #print "%d / %d         " % (a, t)
                #print gobject.main_depth()
                #if (gobject.main_depth() < 3): 
                gtk.main_iteration(False)
                
            else:
                self.emit_message(msgs.MEDIA_EV_DOWNLOAD_PROGRESS, f, a, t)
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

        
        # handle locally saved videos
        if (f.resource.startswith("/")): return f.resource
        
        if (f.resource == _REGION_BLOCKED):
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "You are not allowed to view this!",
                              "You became a victim of internet censorship.\n\n"
                              "MediaBox cannot load this video in your country.")
            return ""
        
        self.emit_message(msgs.UI_ACT_SHOW_MESSAGE,
                        "Requesting Video",
                        "- %s -" % f.name,
                        theme.youtube_device)
            
        try:
            flv, fmts = self.__get_flv(f.resource)
        except:
            logging.error("could not retrieve video\n%s", logging.stacktrace())
            self.emit_message(msgs.UI_ACT_HIDE_MESSAGE)
            return ""

        # download high-quality version, if desired
        qtype = config.get_quality_type()
        print "QType:", qtype, fmts, qtype in fmts
        if (qtype in fmts):
            flv = flv + "&fmt=%d" % qtype
            ext = "." + formats.get_container(qtype)
        else:
            ext = ".flv"
            
        self.emit_message(msgs.UI_ACT_HIDE_MESSAGE)
        logging.info("found FLV: %s", flv)

        if (self.__flv_downloader):
            self.__flv_downloader.cancel()

        cache_folder = config.get_cache_folder()
        flv_path = os.path.join(cache_folder, ".tube.flv")
        keep_path = os.path.join(cache_folder, _VIDEO_FOLDER,
                                 self.__make_filename(f.name, ext))
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


    def delete_file(self, folder, idx):
        """
        Deletes the given file.
        """

        f = self.__items[idx]
        response = dialogs.question("Remove",
                                    u"Remove video\n\xbb%s\xab?" % f.name)
        if (response == 0):
            try:
                os.unlink(f.resource)
            except:
                pass
        
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.__current_folder)


    def keep(self, f):
        """
        Keeps the current video.
        """
        
        self.__keep_video = True
        self.emit_event(msgs.NOTIFY_SVC_SHOW_INFO,
                        u"video will be saved as\n\xbb%s\xab" \
                        % self.__make_filename(f.name, ""))



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

        #return urlquote.quote(name, " ") + ".flv"
        return name + ext


    def __copy_thumbnail(self, f1, path):
    
        f2 = File(self)
        f2.path = "/local" + path

        self.call_service(msgs.MEDIASCANNER_SVC_COPY_THUMBNAIL, f1, f2)

