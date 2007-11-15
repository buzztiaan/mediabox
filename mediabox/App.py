from MainWindow import MainWindow
from viewers.Thumbnail import Thumbnail
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from ui import dialogs
from ControlBar import ControlBar
import panel_actions
from Thumbnailer import Thumbnailer
import config
import viewers
import theme

import gtk
import gobject
import os
import time

try:
    import osso
    _HAVE_OSSO = True
except:
    _HAVE_OSSO = False
    
_OSSO_NAME = "de.pycage.mediabox"
_VERSION = "0.90"
    

class App(object):
    """
    Main class of the application.
    """

    def __init__(self):

        self.__viewers = []
        self.__current_viewer = None
        self.__current_collection = []
        self.__current_mediaroots = []
        
        self.__selected_item_of_viewer = {}
        self.__offset_of_viewer = {}

        self.__saved_image = None
        self.__saved_image_index = -1
    
        if (_HAVE_OSSO):
            self.__osso_context = osso.Context(_OSSO_NAME, _VERSION, False)
    
        # set theme
        theme.set_theme(config.theme())
    
        # window
        self.__window = MainWindow()
        self.__window.set_app_paintable(True)
        self.__window.connect("expose-event", self.__on_expose)
        self.__window.connect("key-press-event", self.__on_key)
        self.__window.connect("key-release-event", lambda x, y: True)        
        self.__window.show()        
       
        # control bar
        self.__ctrlbar = ControlBar()
        self.__ctrlbar.set_size_request(800, 80)
        self.__ctrlbar.add_observer(self.__on_observe_ctrlbar)
        self.__ctrlbar.show()
        self.__window.put(self.__ctrlbar, 0, 400)

        # image strip
        self.__strip = ImageStrip(160, 120, 10)
        self.__strip.set_background(theme.background.subpixbuf(10, 0, 160, 400))
        self.__strip.show()

        self.__kscr = KineticScroller(self.__strip)
        self.__kscr.set_size_request(160, 400)
        self.__kscr.add_observer(self.__on_observe_strip)
        self.__window.put(self.__kscr, 10, 0)

        # box for viewers
        self.__box = gtk.HBox()
        self.__box.set_size_request(620, 400)
        self.__box.show()
        self.__window.put(self.__box, 180, 0)

        
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """
        
        actions = [(self.__load_viewers, []),
                   (self.__check_for_player, []),
                   (self.__scan_media, []),
                   (self.__ctrlbar.select_tab, [0])]
        def f():
            if (actions):
                act, args = actions.pop(0)
                act(*args)
                return True
            else:
                return False
                
        gobject.idle_add(f)
        
        

    def __scan_media(self):
        """
        Scans the media root locations for media files. Will create thumbnails
        when missing.
        """

        mediaroots = config.mediaroot()
        mediaroots.sort()
    
        if (not mediaroots):
            dialogs.warning("No media location specified!",
                 "Please specify the locations of your\n"
                 "media files in the preferences.")
        #end if

        if (`mediaroots` == `self.__current_mediaroots`):
            return
            
        else:
            self.__current_mediaroots = mediaroots


        thumbnailer = Thumbnailer(self.__window)
        thumbnailer.show()
        while (gtk.events_pending()): gtk.main_iteration()

        collection = []
        thumbdir = os.path.abspath(config.thumbdir())
        for mediaroot in mediaroots:
            for dirpath, dirs, files in os.walk(mediaroot):
                # don't allow scanning the thumbnail directory as this may
                # loop endlessly
                if (dirpath == thumbdir): continue

                dirs.sort()
                files.sort()                
                                
                for f in dirs + files:
                    uri = os.path.join(dirpath, f)
                    collection.append(uri)                    
                #end for            
            #end for
        #end for
        
        total = len(collection)
        
        for v in self.__viewers:
            v.clear_items()

        cnt = 0
        for uri in collection:
            cnt += 1
            thumbnailer.set_progress(cnt, total)
            for v in self.__viewers:
                v.make_item_for(uri, thumbnailer)
            #end for
        #end for
        
        thumbnailer.destroy()
        import gc; gc.collect()


    def __load_viewers(self):
        """
        Loads the media viewers.
        """
    
        self.__viewers = viewers.get_viewers()
        cnt = 0
        for viewer in self.__viewers:            
            self.__ctrlbar.add_tab(viewer.ICON, cnt)
            cnt += 1
            
            self.__box.add(viewer.get_widget())
            viewer.add_observer(self.__on_observe_viewer)
            
            while (gtk.events_pending()): gtk.main_iteration()
        #end for
                
        
    def __check_for_player(self):
        """
        Checks if a media player backend is available and tells the user
        if not.
        """
    
        import MPlayer
        mplayer = MPlayer.MPlayer()
        
        if (not mplayer.is_available()):
            dialogs.warning("mplayer was not found!",
                 "Please install mplayer on your\ninternet tablet in order to\n"
                 "be able to play video or audio.")
                        
        

    def __on_expose(self, src, ev):
    
        x, y, w, h = ev.area
        src.window.draw_pixbuf(src.window.new_gc(),
                               theme.background,
                               x, y, x, y, w, h)
                               
                               
    def __on_key(self, src, ev):
    
        keyval = ev.keyval
        key = gtk.gdk.keyval_name(keyval)
        
        if (key == "Escape"):
            self.__try_quit()
        elif (key == "F6"):
            self.__current_viewer.fullscreen()
        elif (key == "F7"):
            self.__current_viewer.increment()
        elif (key == "F8"):
            self.__current_viewer.decrement()
            
        elif (key == "Up"):
            self.__kscr.impulse(0, 7.075)
        elif (key == "Down"):
            self.__kscr.impulse(0, -7.075)
        
            
        return True


    def __on_observe_viewer(self, src, cmd, *args):
            
        if (cmd == src.OBS_REPORT_CAPABILITIES):
            caps = args[0]
            self.__ctrlbar.set_capabilities(caps)
    
        elif (cmd == src.OBS_SCAN_MEDIA):
            self.__scan_media() #gobject.idle_add(self.__scan_media)

        elif (cmd == src.OBS_STATE_PLAYING):
            self.__ctrlbar.set_playing(True)
        
        elif (cmd == src.OBS_STATE_PAUSED):
            self.__ctrlbar.set_playing(False)

        elif (cmd == src.OBS_TITLE):
            title = args[0]
            self.__ctrlbar.set_title(title)
    
        elif (cmd == src.OBS_POSITION):
            pos, total = args
            self.__ctrlbar.set_position(pos, total)
            
        elif (cmd == src.OBS_VOLUME):
            percent = args[0]
            self.__ctrlbar.set_volume(percent)
            
        elif (cmd == src.OBS_SET_COLLECTION):
            items = args[0]
            self.__current_collection = items
            self.__set_collection(items)

            self.__kscr.show()        
            self.__saved_image = None
            self.__saved_image_index = -1
            
        elif (cmd == src.OBS_SHOW_COLLECTION):
            self.__window.move(self.__box, 180, 0)
            self.__box.set_size_request(620, 400)     
            self.__kscr.show()

        elif (cmd == src.OBS_HIDE_COLLECTION):
            self.__window.move(self.__box, 0, 0)
            self.__box.set_size_request(800, 400)
            self.__kscr.hide()

        elif (cmd == src.OBS_FULLSCREEN):
            self.__window.move(self.__box, 0, 0)
            self.__box.set_size_request(800, 480)
            self.__box.set_border_width(0)
            self.__kscr.hide()
            self.__ctrlbar.hide()

        elif (cmd == src.OBS_UNFULLSCREEN):
            self.__window.move(self.__box, 180, 0)
            self.__box.set_size_request(620, 400)
            if (self.__current_viewer):
                self.__box.set_border_width(self.__current_viewer.BORDER_WIDTH)
            self.__kscr.show()
            self.__ctrlbar.show()
            
        elif (cmd == src.OBS_SHOW_MESSAGE):
            msg = args[0]
            self.__ctrlbar.show_message(msg)
            
        elif (cmd == src.OBS_SHOW_PANEL):
            self.__ctrlbar.show_panel()


    def __on_observe_ctrlbar(self, src, cmd, *args):
    
        if (cmd == panel_actions.PLAY_PAUSE):
            self.__current_viewer.play_pause()
    
        elif (cmd == panel_actions.SET_POSITION):
            pos = args[0]
            self.__current_viewer.set_position(pos)
            
        elif (cmd == panel_actions.TAB_SELECTED):
            idx = args[0]
            self.__select_viewer(idx)
                                               

    def __on_observe_strip(self, src, cmd, *args):
    
        def f(ticket, item):
            if (ticket == self.__ticket): self.__media_player.load(item)
            
        if (cmd == src.OBS_SCROLLING):
            # invalidate ticket
            self.__ticket = 0
    
        elif (cmd == src.OBS_CLICKED):
            px, py = args
            if (px < 100): return
            idx = self.__strip.get_index_at(py)            
            self.__select_item(idx)
            
            
    def __select_item(self, idx):

        self.__hilight_item(idx)    

        item = self.__current_collection[idx]        
        self.__selected_item_of_viewer[self.__current_viewer] = idx        
        gobject.idle_add(self.__current_viewer.load, item)


    def __hilight_item(self, idx):
    
        if (self.__saved_image):
            self.__strip.replace_image(self.__saved_image_index,
                                        self.__saved_image)
        self.__saved_image = self.__strip.get_image(idx)
        self.__saved_image_index = idx
        
        hilighted = self.__saved_image.copy()
        theme.selection_frame.composite(hilighted, 0, 0,
                                        hilighted.get_width(),
                                        hilighted.get_height(),
                                        0, 0, 1, 1, gtk.gdk.INTERP_NEAREST,
                                        0xff)
        
        self.__strip.replace_image(idx, hilighted)
        

            
    def __select_viewer(self, idx):
        """
        Selects the current viewer by index number.
        """
    
        viewer = self.__viewers[idx]
        if (self.__current_viewer and self.__current_viewer != viewer):
            self.__current_viewer.hide()
            self.__offset_of_viewer[self.__current_viewer] = \
                self.__strip.get_offset()
                
        self.__current_viewer = viewer
        self.__box.set_border_width(viewer.BORDER_WIDTH)
        
        def f():
            viewer.show()
            offset = self.__offset_of_viewer.get(viewer, 0)
            item_idx = self.__selected_item_of_viewer.get(viewer, -1)
            self.__strip.set_offset(offset)
            if (item_idx >= 0):
                self.__hilight_item(item_idx)

        gobject.idle_add(f)



    def __set_collection(self, collection):
        """
        Loads the given collection into the item strip.
        """

        thumbnails = [ item.get_thumbnail() for item in collection ]                
        self.__strip.set_images(thumbnails)
        
        # initialize thumbnails with deferred rendering
        #for t in thumbnails: t.get_width()        
        


    def run(self):
        """
        Runs the application.
        """
            
        self.__startup()
        gtk.main()
        
        print "HALTING MPLAYER"
        import MPlayer
        MPlayer.MPlayer().close()
        
        
        
    def __try_quit(self):
    
        result = dialogs.question("Exit", "Really quit?")
        if (result == 0):
            gtk.main_quit()
 
