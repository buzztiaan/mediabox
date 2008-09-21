from com import Viewer, msgs

from VideoThumbnail import VideoThumbnail
from mediabox import viewmodes
from ui import dialogs
import theme

import gobject
import os



class VideoViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_video
    PRIORITY = 10


    def __init__(self):
    
        self.__is_fullscreen = False
    
        self.__items = []
        self.__thumbnails_needed = []
        self.__video_widget = None
        self.__uri = ""


        Viewer.__init__(self)                

                
        
    def render_this(self):
        
        if (not self.__video_widget):
            self.__video_widget = self.call_service(
                                      msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                                      self, "video/*")
            self.add(self.__video_widget)            
            self.__video_widget.connect_fullscreen_toggled(self.__on_fullscreen)
            self.__video_widget.connect_media_position(self.__on_media_position)
            self.__video_widget.connect_media_volume(self.__on_media_volume)
            self.set_toolbar(self.__video_widget.get_controls())
   
        if (self.__is_fullscreen):
            x, y = 0, 0
            w, h = self.get_size()
        else:
            x, y, w, h = self.__get_frame_rect()

        self.__video_widget.set_geometry(x, y, w, h)
    


    def handle_event(self, event, *args):
    
        if (event == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__update_media()
    
        elif (event == msgs.MEDIA_EV_PLAY):
            pass
            #self.__player.stop()

        elif (event == msgs.MEDIA_ACT_STOP):
            if (self.__video_widget):
                self.__video_widget.stop()
    
        if (self.is_active()):
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                item = self.__items[idx]
                self.__load(item)

            elif (event == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)     

            elif (event == msgs.HWKEY_EV_INCREMENT):
                self.__on_increment()
                
            elif (event == msgs.HWKEY_EV_DECREMENT):
                self.__on_decrement()

            elif (event == msgs.HWKEY_EV_FULLSCREEN):
                self.__on_fullscreen()
                
        #end if
            


    def __on_media_position(self, info):
    
        self.set_info(info)


    def __on_media_volume(self, volume):
        """
        Reacts on changing the sound volume.
        """

        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)
        
            
    """
    def __on_observe_player(self, src, cmd, *args):
    
        if (not self.is_active()): return            
            
        if (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
            #self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__uri = ""
            self.set_title("")
            self.__screen.hide()
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
            #self.update_observer(self.OBS_STATE_PAUSED)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__show_error(err)
                self.set_title("")
                self.__screen.hide()
            
        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.__btn_play.set_images(theme.btn_pause_1,
                                           theme.btn_pause_2)                
                #self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)
                #self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args            
            if (not self.__is_fullscreen and ctx == self.__context_id):
                pos_m = pos / 60
                pos_s = pos % 60
                total_m = total / 60
                total_s = total % 60
                info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)
                self.set_info(info)

                self.__progress.set_position(pos, total)

        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                self.__uri = ""
                self.__screen.hide()

                # unfullscreen
                if (self.__is_fullscreen): self.__on_fullscreen()
                
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)                
                #self.update_observer(self.OBS_STATE_PAUSED)
           
        elif (cmd == src.OBS_ASPECT):
            ctx, ratio = args            
            self.__aspect_ratio = ratio
            self.__set_aspect_ratio(ratio)
            self.__screen.show()
    """

    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            dialogs.error("Not supported", "The media format is not supported.")


    def __get_frame_rect(self):
    
        w, h = self.get_size()
        return (2, 2, w - 14, h - 4)
            

    def clear_items(self):
    
        self.__items = []


    def __load_thumbnails(self, tn_list):
    
        def on_thumbnail(thumb, tn, files):
            tn.set_thumbnail(thumb)
            tn.invalidate()
            self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)
            
            if (tn_list):
                f, tn = tn_list.pop(0)
                gobject.idle_add(self.call_service,
                  msgs.MEDIASCANNER_SVC_SCAN_FILE, f, on_thumbnail, tn, tn_list)
        
        f, tn = tn_list.pop(0)
        self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                          on_thumbnail, tn, tn_list)



    def __update_media(self):
        
        self.__items = []
        thumbnails = []
        
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["video/"])        
        files = []
        self.__thumbnails_needed = []
        for f in media:
            thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
            tn = VideoThumbnail(thumb, f.name)
            tn.set_emblem(f.source_icon)
            self.__items.append(f)
            thumbnails.append(tn)

            if (not os.path.exists(thumb)):
                self.__thumbnails_needed.append((f, tn))
        #end for
        
        self.set_collection(thumbnails)

        

    def __load(self, item):

        self.emit_event(msgs.MEDIA_ACT_STOP)
        self.emit_event(msgs.MEDIA_EV_PLAY)
    
        def f():
            uri = item.resource
            if (uri == self.__uri): return
            
            self.__video_widget.load(item)
            self.set_title(os.path.basename(uri))
            self.__uri = uri

        gobject.idle_add(f)
        self.emit_event(msgs.MEDIA_EV_LOADED, self, item)
                       

    def __on_increment(self):
    
        self.__video_widget.increment()
        
        
    def __on_decrement(self):

        self.__video_widget.decrement()


    def __on_fullscreen(self):
              
        self.__is_fullscreen = not self.__is_fullscreen        
        
        if (self.__is_fullscreen):
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.render()
        else:
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)            
            self.render()
            gobject.idle_add(self.emit_event, msgs.CORE_ACT_RENDER_ALL)


    def show(self):
    
        Viewer.show(self)
        if (self.__thumbnails_needed):
            self.__load_thumbnails(self.__thumbnails_needed)
            
            
    def __search(self, key):

        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.emit_event(msgs.CORE_ACT_SELECT_ITEM, idx)
                print "found", item.name, "for", key
                break
            idx += 1
        #end for
