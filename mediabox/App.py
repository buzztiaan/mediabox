from MainWindow import MainWindow
from SplashScreen import SplashScreen
from RootPane import RootPane
from ContentPane import ContentPane
from Thumbnailer import Thumbnailer
from ViewerState import ViewerState
from viewers.Thumbnail import Thumbnail
from ui.Pixmap import Pixmap
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from ui import dialogs
from ControlBar import ControlBar
import panel_actions
from mediascanner.MediaScanner import MediaScanner
import config
import values
import viewers
import theme

import gtk
import gobject
import os
import time

try:
    import osso
    import hildon
    _HAVE_OSSO = True
except:
    _HAVE_OSSO = False
    

class App(object):
    """
    Main class of the application.
    """

    def __init__(self):

        self.__viewers = []
        self.__current_viewer = None
        self.__current_collection = []
        self.__current_mediaroots = []
        
        # mapping: viewer -> state
        self.__viewer_states = {}

        self.__saved_image = None
        self.__saved_image_index = -1
    
        if (_HAVE_OSSO):
            self.__osso_context = osso.Context(values.OSSO_NAME, values.VERSION, False)
            self.__program = hildon.Program()
    
        # set theme
        try:
            theme.set_theme(config.theme())
        except:
            # theme could not be loaded
            pass
            
    
        # window
        self.__window = MainWindow()
        self.__window.set_app_paintable(True)
        self.__window.connect("delete-event", self.__on_close_window)
        self.__window.connect("expose-event", self.__on_expose)
        self.__window.connect("key-press-event", self.__on_key)
        self.__window.connect("key-release-event", lambda x, y: True)
        self.__window.show()    
        
        if (_HAVE_OSSO):
            self.__program.add_window(self.__window)

        # screen pixmap
        self.__screen = Pixmap(self.__window.window)
        self.__screen.draw_pixbuf(theme.background, 0, 0)

        # root pane
        self.__root_pane = RootPane(self.__window)
        self.__root_pane.set_screen(self.__screen)

        # splash screen
        self.__splash = SplashScreen(self.__window)
        self.__splash.set_visible(True)
        self.__root_pane.add(self.__splash)

        # thumbnail screen
        self.__thumbnailer = Thumbnailer(self.__window)
        self.__thumbnailer.set_visible(False)
        self.__root_pane.add(self.__thumbnailer)
        
        # content pane
        self.__content_pane = ContentPane(self.__window)
        self.__root_pane.add(self.__content_pane)
        self.__content_pane.set_visible(False)
        
        # control bar
        self.__ctrlbar = ControlBar(self.__window)
        self.__ctrlbar.set_pos(0, 400)
        self.__ctrlbar.add_observer(self.__on_observe_ctrlbar)
        self.__root_pane.add(self.__ctrlbar)
       
        # image strip
        self.__strip = ImageStrip(self.__window, 160, 120, 10)
        self.__strip.set_pos(10, 0)
        self.__strip.set_size(160, 400)
        self.__strip.set_background(theme.background.subpixbuf(10, 0, 160, 400))
        self.__content_pane.add(self.__strip)

        self.__kscr = KineticScroller(self.__strip)
        self.__kscr.set_touch_area(0, 108)
        self.__kscr.add_observer(self.__on_observe_strip)

        # set up media scanner
        mscanner = MediaScanner()
        mscanner.add_observer(self.__on_observe_media_scanner)
      
       
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """
        
        actions = [(self.__root_pane.render, []),
                   (self.__load_viewers, []),
                   (self.__check_for_player, []),
                   #(time.sleep, [500]),
                   (self.__splash.set_visible, [False]),
                   (self.__content_pane.set_visible, [True]),
                   (self.__ctrlbar.set_visible, [True]),                   
                   (self.__root_pane.render, []),
                   (self.__scan_media, []),
                   (self.__ctrlbar.select_tab, [0]),
                   ]
                   
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
    
        if (`mediaroots` == `self.__current_mediaroots`):
            return
        else:
            self.__current_mediaroots = mediaroots

        if (not mediaroots):
            dialogs.warning("No media location specified!",
                            "Please specify the locations of your\n"
                            "media files in the preferences.")
            return
        #end if


        self.__ctrlbar.show_message("Looking for media files...")
        self.__content_pane.set_visible(False)
        self.__thumbnailer.clear()
        self.__thumbnailer.set_visible(True)
        self.__root_pane.render()
        while (gtk.events_pending()): gtk.main_iteration()


        mscanner = MediaScanner()
        mscanner.set_thumb_folder(os.path.abspath(config.thumbdir()))
        
        # TODO: media types should be applied by the user to the roots
        #mtypes = mscanner.MEDIA_VIDEO | \
        #         mscanner.MEDIA_AUDIO | \
        #         mscanner.MEDIA_IMAGE
        
        mscanner.set_media_roots(mediaroots) #[ (uri, mtypes) for uri in mediaroots ])

        now = time.time()
        mscanner.scan()

        #self.__ctrlbar.show_message("Took %f seconds" % (time.time() - now))
        #while (gtk.events_pending()): gtk.main_iteration()

        self.__ctrlbar.show_message("Generating Thumbnails...")
        while (gtk.events_pending()): gtk.main_iteration()

        # update viewers        
        now = time.time()
        for v in self.__viewers:
            v.update_media(mscanner)
            self.__viewer_states[v].thumbs_loaded = False
            self.__viewer_states[v].selected_item = -1
            self.__viewer_states[v].item_offset = 0

        self.__thumbnailer.set_visible(False)
        self.__content_pane.set_visible(True)
        self.__root_pane.render()

        import gc; gc.collect()
        self.__ctrlbar.show_panel()                
        


    def __load_viewers(self):
        """
        Loads the media viewers.
        """
    
        cnt = 0
        for viewerclass in viewers.get_viewers():
            try:
                viewer = viewerclass(self.__window)
            except:
                import traceback; traceback.print_exc()
                continue

            self.__ctrlbar.add_tab(viewer.ICON, viewer.ICON_ACTIVE, cnt)
            cnt += 1

            self.__content_pane.add(viewer)
            viewer.set_visible(False)
            viewer.set_pos(180, 0)
            viewer.set_size(620, 400)
            viewer.add_observer(self.__on_observe_viewer)
            
            vstate = ViewerState()
            vstate.caps = viewer.CAPS
            self.__viewer_states[viewer] = vstate
            self.__viewers.append(viewer)
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
                        
                        
    def __on_close_window(self, src, ev):
    
        self.__try_quit()
        return True
        

    def __on_expose(self, src, ev):
    
        x, y, w, h = ev.area
        self.__screen.restore(x, y, w, h)


    def __on_key(self, src, ev):
    
        keyval = ev.keyval
        key = gtk.gdk.keyval_name(keyval)
        
        if (key == "Escape"):
            self.__try_quit()
        elif (key == "Return"):
            self.__current_viewer.do_enter()
        elif (key == "F6"):
            self.__current_viewer.do_fullscreen()
        elif (key == "F7"):
            self.__current_viewer.do_increment()
        elif (key == "F8"):
            self.__current_viewer.do_decrement()
            
        elif (key == "Up"):
            self.__kscr.impulse(0, 7.075)
        elif (key == "Down"):
            self.__kscr.impulse(0, -7.075)
        else:
            print "unknown key", key
            
        return True


    def __on_observe_media_scanner(self, src, cmd, *args):
    
        if (cmd == src.OBS_THUMBNAIL_GENERATED):
            thumburi, uri = args
            name = os.path.basename(uri)
            self.__thumbnailer.show_thumbnail(thumburi, name)



    def __on_observe_viewer(self, src, cmd, *args):
            
        if (cmd == src.OBS_MINIMIZE):
            self.__window.iconify()
            
        elif (cmd == src.OBS_QUIT):
            self.__try_quit()
            
        elif (cmd == src.OBS_REPORT_CAPABILITIES):
            caps = args[0]
            self.__ctrlbar.set_capabilities(caps)
            self.__get_vstate().caps = caps
    
        elif (cmd == src.OBS_SCAN_MEDIA):
            force = args[0]
            if (force): self.__current_mediaroots = []
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
            
        elif (cmd == src.OBS_FREQUENCY_MHZ):
            freq = args[0]
            unit = "MHz"
            self.__ctrlbar.set_value(freq, unit)
            
        elif (cmd == src.OBS_VOLUME):
            percent = args[0]
            self.__ctrlbar.set_volume(percent)
            
        elif (cmd == src.OBS_SET_COLLECTION):
            items = args[0]
            self.__current_collection = items
            self.__set_collection(items)

            self.__saved_image = None
            self.__saved_image_index = -1
           
        elif (cmd == src.OBS_SELECT_ITEM):
            idx = args[0]
            self.__select_item(idx)
            
        elif (cmd == src.OBS_RENDER):
            self.__root_pane.render_buffered()
            
        elif (cmd == src.OBS_SHOW_COLLECTION):
            #if (not self.__strip.is_visible()):
            self.__strip.set_visible(True)
            #self.__strip.render()
            #self.__strip.fx_slide_in()
            self.__get_vstate().collection_visible = True
            self.__current_viewer.set_pos(180, 0)
            #self.__content_pane.render()

        elif (cmd == src.OBS_HIDE_COLLECTION):
            self.__strip.set_visible(False)
            #self.__strip.fx_slide_out()
            self.__get_vstate().collection_visible = False
            self.__current_viewer.set_pos(0, 0)
            #self.__content_pane.render()

        elif (cmd == src.OBS_FULLSCREEN):
            self.__strip.set_visible(False)
            self.__ctrlbar.set_visible(False)
            #self.__strip.fx_slide_out(wait = False)
            #self.__ctrlbar.fx_lower()
            self.__current_viewer.set_pos(0, 0)
            self.__current_viewer.set_size(800, 480)
            #self.__current_viewer.render()
            #self.__root_pane.render()

        elif (cmd == src.OBS_UNFULLSCREEN):
            self.__strip.set_visible(True)
            self.__ctrlbar.set_visible(True)
            #self.__strip.render()
            #self.__ctrlbar.render()
            #self.__strip.fx_slide_out(wait = False)
            #self.__ctrlbar.fx_lower()
            self.__current_viewer.set_pos(180, 0)
            self.__current_viewer.set_size(620, 400)
            #self.__current_viewer.render()
            #self.__root_pane.render()
            #self.__ctrlbar.render()
            
        elif (cmd == src.OBS_SHOW_MESSAGE):
            msg = args[0]
            self.__ctrlbar.show_message(msg)
            
        elif (cmd == src.OBS_SHOW_PROGRESS):
            value, total = args
            self.__ctrlbar.show_progress("Loading...", value, total)
            
        elif (cmd == src.OBS_SHOW_PANEL):
            self.__ctrlbar.show_panel()


    def __on_observe_ctrlbar(self, src, cmd, *args):
    
        if (cmd == panel_actions.PLAY_PAUSE):
            self.__current_viewer.do_play_pause()

        elif (cmd == panel_actions.ZOOM_IN):
            self.__current_viewer.do_zoom_in()

        elif (cmd == panel_actions.ZOOM_OUT):
            self.__current_viewer.do_zoom_out()

        elif (cmd == panel_actions.ZOOM_100):
            self.__current_viewer.do_zoom_100()

        elif (cmd == panel_actions.ZOOM_FIT):
            self.__current_viewer.do_zoom_fit()

        elif (cmd == panel_actions.PREVIOUS):
            self.__current_viewer.do_previous()

        elif (cmd == panel_actions.NEXT):
            self.__current_viewer.do_next()
            
        elif (cmd == panel_actions.ADD):
            self.__current_viewer.do_add()
    
        elif (cmd == panel_actions.SET_POSITION):
            pos = args[0]
            self.__current_viewer.do_set_position(pos)
            
        elif (cmd == panel_actions.TUNE):
            pos = args[0]
            self.__current_viewer.do_tune(pos)
            
        elif (cmd == panel_actions.TAB_SELECTED):
            idx = args[0]
            self.__select_viewer(idx)
                                               

    def __on_observe_strip(self, src, cmd, *args):
    
        if (cmd == src.OBS_SCROLLING):
            # invalidate ticket
            self.__ticket = 0
    
        elif (cmd == src.OBS_CLICKED):
            px, py = args
            if (px > 108):
                idx = self.__strip.get_index_at(py)            
                self.__select_item(idx)
           
           
    def __get_vstate(self):
    
        return self.__viewer_states[self.__current_viewer]
            
            
    def __select_item(self, idx):

        self.__hilight_item(idx)

        item = self.__current_collection[idx]
        self.__get_vstate().selected_item = idx
        self.__current_viewer.load(item)
        self.__strip.scroll_to_item(idx)


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
        
        if (self.__current_viewer):
            self.__current_viewer.hide()
            self.__get_vstate().item_offset = self.__strip.get_offset()
                
        self.__current_viewer = viewer
        self.__kscr.stop_scrolling()

        buf = Pixmap(None, 800, 400)
        self.__content_pane.set_screen(buf)

        vstate = self.__get_vstate()
        if (vstate.collection_visible):
            viewer.set_pos(180, 0)
            viewer.set_size(620, 400)
            self.__strip.set_visible(True)
        else:
            viewer.set_pos(0, 0)
            viewer.set_size(800, 400)
            self.__strip.set_visible(False)
        
        def f():
            viewer.show()
            self.__ctrlbar.set_capabilities(vstate.caps)
            
            offset = vstate.item_offset
            item_idx = vstate.selected_item
            self.__strip.set_offset(offset)
            if (item_idx >= 0):
                self.__hilight_item(item_idx)

            self.__content_pane.render()
            self.__content_pane.set_screen(self.__screen)
            self.__content_pane.fx_raise(buf)

        gobject.idle_add(f)



    def __set_collection(self, collection):
        """
        Loads the given collection into the item strip.
        """

        thumbnails = [ item.get_thumbnail() for item in collection ]                
        
        vstate = self.__get_vstate()        
        if (not vstate.thumbs_loaded):
            total = len(thumbnails)
            cnt = 1
            for t in thumbnails:
                t.get_width()

                if (cnt % 5 == 0 or (cnt == total and cnt > 5)):
                    self.__ctrlbar.show_progress("Loading %d Items..." % total,
                                                 cnt, total)                
                    while (gtk.events_pending()): gtk.main_iteration()
                    
                cnt += 1                    
            #end for
        #end if

        self.__strip.set_images(thumbnails)

        if (not vstate.thumbs_loaded):
            vstate.thumbs_loaded = True
            

    def run(self):
        """
        Runs the application.
        """
            
        self.__startup()
        gtk.main()
        
        
        
    def __try_quit(self):
    
        result = dialogs.question("Exit", "Really quit?")
        if (result == 0):
            for v in self.__viewers:
                v.shutdown()
            gtk.main_quit()

