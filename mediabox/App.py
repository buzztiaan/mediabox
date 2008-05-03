from MainWindow import MainWindow
from SplashScreen import SplashScreen
from RootPane import RootPane
from TitlePanel import TitlePanel
from ControlPanel import ControlPanel
from TabPanel import TabPanel
from WindowControls import WindowControls
from Thumbnailer import Thumbnailer
from ViewerState import ViewerState
from viewers.Thumbnail import Thumbnail
from ui.HBox import HBox
from ui.VBox import VBox
from ui.Image import Image
from ui.Pixmap import Pixmap
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from ui import pixbuftools
from ui import dialogs
import panel_actions
from Headset import Headset
from mediascanner.MediaScanner import MediaScanner
import config
import values
import viewers
from utils import maemo
import theme

import gtk
import gobject
import os
import time


_MODE_NORMAL = 0
_MODE_NO_STRIP = 1
_MODE_FULLSCREEN = 2
_MODE_TITLE_ONLY = 3


class App(object):
    """
    Main class of the application.
    """

    def __init__(self):

        self.__viewers = []
        self.__current_viewer = None
        self.__current_collection = []
        self.__current_mediaroots = []
        self.__view_mode = _MODE_TITLE_ONLY
        
        # mapping: viewer -> state
        self.__viewer_states = {}

        self.__saved_image = None
        self.__saved_image_index = -1
        
        # flag for indicating whether media scanning has already been scheduled
        self.__media_scan_scheduled = False
    
        # search string for finding items with the keyboard
        self.__keyboard_search_string = ""
        # time after which the keyboard search string gets reset
        self.__keyboard_search_reset_time = 0
    
        if (maemo.IS_MAEMO):
            import hildon
            import osso
            maemo.set_osso_context(osso.Context(values.OSSO_NAME,
                                                "1.0", False))
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
        
        if (maemo.IS_MAEMO):
            self.__program.add_window(self.__window)

        # screen pixmap
        self.__screen = Pixmap(self.__window.window)
        #self.__screen.draw_pixbuf(theme.background, 0, 0)

        # root pane
        self.__root_pane = RootPane(self.__window)
        self.__root_pane.set_screen(self.__screen)

        # splash screen
        self.__splash = SplashScreen(self.__window)
        self.__splash.set_visible(True)
        self.__root_pane.add(self.__splash)

        left_top = pixbuftools.make_frame(theme.panel, 170, 40, True,
                                          pixbuftools.LEFT |
                                          pixbuftools.BOTTOM)
        left_bottom = pixbuftools.make_frame(theme.panel, 170, 70, True,
                                          pixbuftools.TOP |
                                          pixbuftools.LEFT)
        pixbuftools.draw_pbuf(left_bottom, theme.btn_turn_1, 30, 15)


        # image strip       
        self.__strip = ImageStrip(self.__window, 10)
        self.__strip.set_geometry(0, 0, 170, 480)
        #self.__strip.set_caps(theme.panel_top_left, theme.panel_left)
        self.__strip.set_caps(left_top, left_bottom)
        self.__strip.set_bg_color(theme.color_bg)
        self.__strip.set_visible(False)
        self.__root_pane.add(self.__strip)

        self.__kscr = KineticScroller(self.__strip)
        self.__kscr.set_touch_area(0, 108)
        self.__kscr.add_observer(self.__on_observe_strip)

        # thumbnail screen
        self.__thumbnailer = Thumbnailer(self.__window)
        self.__thumbnailer.set_visible(False)
        self.__root_pane.add(self.__thumbnailer)

        # title panel
        self.__title_panel_left = Image(self.__window, left_top)
        self.__title_panel_left.set_geometry(0, 0, 170, 40)
        self.__title_panel_left.set_visible(False)
        
        self.__title_panel = TitlePanel(self.__window)
        self.__title_panel.set_geometry(170, 0, 630, 40)
        self.__title_panel.set_title("Initializing")
        self.__title_panel.set_visible(False)       
       
        # control panel
        self.__panel_left = Image(self.__window, left_bottom)
        self.__panel_left.set_geometry(0, 410, 160, 70)
        self.__panel_left.connect(self.__panel_left.EVENT_BUTTON_PRESS,
                                  self.__on_menu_button)
        self.__panel_left.set_visible(False)
        
        self.__ctrl_panel = ControlPanel(self.__window)
        self.__ctrl_panel.set_geometry(170, 410, 630, 70)
        self.__ctrl_panel.set_bg(theme.panel)
        self.__ctrl_panel.add_observer(self.__on_observe_ctrlbar)
        self.__ctrl_panel.set_visible(False)

        # tab panel and window controls
        self.__tab_panel = TabPanel(self.__window)
        self.__tab_panel.set_geometry(0, 330, 800, 150)
        self.__tab_panel.set_visible(False)
        self.__tab_panel.add_observer(self.__on_observe_tabs)
        
        self.__window_ctrls = WindowControls(self.__window)
        self.__window_ctrls.set_geometry(600, 0, 200, 80)
        self.__window_ctrls.set_visible(False)
        self.__window_ctrls.add_observer(self.__on_observe_window_ctrls)
        

        # set up media scanner
        mscanner = MediaScanner()
        mscanner.add_observer(self.__on_observe_media_scanner)
             
       
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """
        
        actions = [(self.__root_pane.render_buffered, []),
                   (self.__load_viewers, []),
                   (self.__root_pane.add, [self.__tab_panel]),
                   (self.__root_pane.add, [self.__window_ctrls]),                   
                   (self.__add_panels, []),
                   (self.__splash.set_visible, [False]),                   
                   (self.__root_pane.render_buffered, []),
                   (self.__scan_media, [True]),
                   (self.__select_viewer, [0]),
                   (self.__setup_mmc_replacement_detection, []),
                   (Headset().add_observer, [self.__on_observe_headset]),
                   ]
                   
        def f():
            if (actions):
                act, args = actions.pop(0)
                try:
                    act(*args)
                except:
                    import traceback; traceback.print_exc()
                    pass
                return True
            else:
                return False
                
        gobject.idle_add(f)


    def __add_panels(self):
        """
        Adds the panel components.
        """
    
        self.__root_pane.add(self.__title_panel_left)
        self.__root_pane.add(self.__title_panel)
        self.__root_pane.add(self.__panel_left)
        self.__root_pane.add(self.__ctrl_panel)
        
        
    def __set_view_mode(self, view_mode):
        """
        Sets the view mode.
        """

        if (view_mode == _MODE_NORMAL):
            self.__title_panel_left.set_visible(False)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(True)
            self.__strip.set_visible(True)
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(180, 0, 620, 480)
            
        elif (view_mode == _MODE_NO_STRIP):
            self.__title_panel_left.set_visible(True)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(True)
            self.__ctrl_panel.set_visible(True)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 0, 800, 480)
            
        elif (view_mode == _MODE_FULLSCREEN):
            self.__title_panel_left.set_visible(False)
            self.__title_panel.set_visible(False)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(False)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 0, 800, 480)

        elif (view_mode == _MODE_TITLE_ONLY):
            self.__title_panel_left.set_visible(True)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(False)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 0, 800, 480)

                
        self.__view_mode = view_mode

            
    def __setup_mmc_replacement_detection(self):

        import dbus, dbus.glib
        bus = dbus.SessionBus()
        obj = bus.get_object("org.gnome.GnomeVFS.Daemon",
                             "/org/gnome/GnomeVFS/Daemon")
        iface = dbus.Interface(obj, 'org.gnome.GnomeVFS.Daemon')
        iface.connect_to_signal("VolumeMountedSignal", self.__on_mount_mmc)

      
    def __on_mount_mmc(self, arg):
    
        def f():
            self.__scan_media(True)
            self.__media_scan_scheduled = False
    
        if (not self.__media_scan_scheduled):
            self.__media_scan_scheduled = True
            gobject.timeout_add(500, f)


    def __on_menu_button(self, px, py):
        """
        Reacts on pressing the menu button.
        """
        
        self.__show_tabs()


    def __show_tabs(self):

        self.__root_pane.set_enabled(False)
        self.__root_pane.set_frozen(True)
        
        self.__tab_panel.set_enabled(True)
        self.__tab_panel.set_frozen(False)
        self.__tab_panel.set_visible(True)
        
        self.__tab_panel.fx_raise()

        self.__window_ctrls.set_frozen(False)
        self.__window_ctrls.set_enabled(True)        
        self.__window_ctrls.set_visible(True)
        self.__window_ctrls.fx_slide_in()



    def __scan_media(self, force_scan):
        """
        Scans the media root locations for media files. Will create thumbnails
        when missing.
        """

        if (force_scan):
            self.__current_mediaroots = []

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


        view_mode = self.__view_mode
        self.__set_view_mode(_MODE_TITLE_ONLY)
        if (self.__current_viewer):
            self.__current_viewer.set_visible(False)
        self.__thumbnailer.clear()        
        self.__thumbnailer.set_visible(True)
        self.__root_pane.render_buffered()
        while (gtk.events_pending()): gtk.main_iteration()


        mscanner = MediaScanner()
        mscanner.set_thumb_folder(os.path.abspath(config.thumbdir()))
               
        mscanner.set_media_roots(mediaroots)

        now = time.time()
        mscanner.scan()

        #self.__ctrlbar.show_message("Took %f seconds" % (time.time() - now))
        #while (gtk.events_pending()): gtk.main_iteration()

        while (gtk.events_pending()): gtk.main_iteration()

        # update viewers        
        now = time.time()
        for v in self.__viewers:
            v.update_media(mscanner)
            self.__viewer_states[v].thumbs_loaded = False
            self.__viewer_states[v].selected_item = -1
            self.__viewer_states[v].item_offset = 0

        self.__set_view_mode(view_mode)
        if (self.__current_viewer):
            self.__current_viewer.set_visible(True)        
        self.__thumbnailer.set_visible(False)
        self.__root_pane.render_buffered()

        import gc; gc.collect()
        


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

            self.__tab_panel.add_viewer(viewer)
            #self.__ctrlbar.add_tab(viewer.ICON, viewer.ICON_ACTIVE, cnt)
            cnt += 1

            self.__root_pane.add(viewer)
            viewer.set_visible(False)
            #viewer.set_geometry(180, 0, 620, 480)
            viewer.add_observer(self.__on_observe_viewer)
            
            vstate = ViewerState()
            vstate.caps = viewer.CAPS
            self.__viewer_states[viewer] = vstate
            self.__viewers.append(viewer)
        #end for
                
                               
                        
    def __on_close_window(self, src, ev):
    
        self.__try_quit()
        return True
        

    def __on_expose(self, src, ev):
    
        x, y, w, h = ev.area
        self.__screen.restore(x, y, w, h)


    def __on_key(self, src, ev):

        # show memory consumption      
        import os
        pid = os.getpid()
        size = int(open("/proc/%d/status" % pid, "r").read().splitlines()[15].split()[1])
        size /= 1024.0
        print "Current Resident Set Size: %0.02f MB" % size
                
    
        if (not self.__root_pane.is_enabled()): return
    
        keyval = ev.keyval
        key = gtk.gdk.keyval_name(keyval)
        
        if (key == "space"): key = " "
        
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
            
        elif (key == "XF86Headset"):
            self.__current_viewer.do_enter()
        
        elif (key == "BackSpace"):
            now = time.time()        
            if (now >= self.__keyboard_search_reset_time):
                self.__keyboard_search_string = ""

            if (self.__keyboard_search_string):
                self.__keyboard_search_string = \
                  self.__keyboard_search_string[:-1]

            self.__keyboard_search_reset_time = now + 2

            self.__title_panel.set_title_with_timeout("Search: " + \
                                             self.__keyboard_search_string,
                                             2000)

            if (self.__keyboard_search_string):
                self.__current_viewer.search(self.__keyboard_search_string)

        
        elif (len(key) == 1 and ord(key) > 31):
            now = time.time()
            if (now >= self.__keyboard_search_reset_time):
                self.__keyboard_search_string = ""
                
            self.__keyboard_search_string += key.lower()
            self.__keyboard_search_reset_time = now + 2

            self.__title_panel.set_title_with_timeout("Search: " + \
                                             self.__keyboard_search_string,
                                             2000)

            self.__current_viewer.search(self.__keyboard_search_string)
            
        
        else:
            print "unknown key", key
            
        return True


    def __on_observe_media_scanner(self, src, cmd, *args):
    
        if (cmd == src.OBS_THUMBNAIL_GENERATED):
            thumburi, uri = args
            name = os.path.basename(uri)
            self.__title_panel.set_title(name)
            self.__thumbnailer.show_thumbnail(thumburi, name)


    def __on_observe_window_ctrls(self, src, cmd, *args):
    
        if (cmd == src.OBS_MINIMIZE_WINDOW):
            self.__window.iconify()
            
        elif (cmd == src.OBS_CLOSE_WINDOW):
            self.__try_quit()


    def __on_observe_tabs(self, src, cmd, *args):
    
        if (cmd == src.OBS_TAB_SELECTED):
            idx = args[0]
            #self.__tab_panel.fx_lower()

            self.__window_ctrls.set_visible(False)
            self.__window_ctrls.fx_slide_out()
            self.__tab_panel.set_visible(False)

            if (self.__viewers[idx] != self.__current_viewer):
                #self.__root_pane.fx_fade_out()
                self.__root_pane.set_enabled(True)
                self.__root_pane.set_frozen(False)
                self.__select_viewer(idx)
            else:
                self.__tab_panel.fx_lower()
                self.__root_pane.set_enabled(True)
                self.__root_pane.set_frozen(False)


    def __on_observe_viewer(self, src, cmd, *args):
            
        #if (cmd == src.OBS_MINIMIZE):
        #    self.__window.iconify()
            
        #elif (cmd == src.OBS_QUIT):
        #    self.__try_quit()
            
        if (cmd == src.OBS_REPORT_CAPABILITIES):
            caps = args[0]
            if (src.is_active() and caps != self.__get_vstate().caps):
                self.__ctrl_panel.set_capabilities(caps)
                self.__get_vstate().caps = caps
    
        elif (cmd == src.OBS_SCAN_MEDIA):
            force = args[0]
            self.__scan_media(force)

        elif (cmd == src.OBS_STATE_PLAYING):
            if (src.is_active()):
                self.__ctrl_panel.set_playing(True)
        
        elif (cmd == src.OBS_STATE_PAUSED):
            if (src.is_active()):        
                self.__ctrl_panel.set_playing(False)

        elif (cmd == src.OBS_TITLE):
            title = args[0]
            if (src.is_active()):
                self.__title_panel.set_title(title)
                self.__get_vstate().title = title
    
        elif (cmd == src.OBS_TIME):
            pos, total = args
            pos_m = pos / 60
            pos_s = pos % 60
            total_m = total / 60
            total_s = total % 60
            info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)
            if (src.is_active()):
                self.__title_panel.set_info(info)
                self.__ctrl_panel.set_position(pos, total)
                self.__get_vstate().info = info
    
        elif (cmd == src.OBS_POSITION):
            pos, total = args
            info = "%d / %d" % (pos, total)
            if (src.is_active()):
                self.__title_panel.set_info(info)
                self.__get_vstate().info = info
            
        elif (cmd == src.OBS_FREQUENCY_MHZ):
            freq = args[0]
            info = "%03.2f MHz" % freq
            if (src.is_active()):
                self.__title_panel.set_info(info)
                #self.__ctrl_panel.set_value(freq, unit)
                self.__get_vstate().info = info
            
        elif (cmd == src.OBS_VOLUME):
            percent = args[0]
            self.__title_panel.set_volume(percent)
            
        elif (cmd == src.OBS_SET_COLLECTION):
            items = args[0]
            if (src.is_active()):
                self.__current_collection = items
                self.__set_collection(items)

                self.__saved_image = None
                self.__saved_image_index = -1
           
        elif (cmd == src.OBS_SELECT_ITEM):
            idx = args[0]
            if (src.is_active()):
                self.__select_item(idx)
            
        elif (cmd == src.OBS_RENDER):
            self.__root_pane.render_buffered()
            
        elif (cmd == src.OBS_SHOW_COLLECTION):
            self.__set_view_mode(_MODE_NORMAL)
            self.__get_vstate().collection_visible = True

        elif (cmd == src.OBS_HIDE_COLLECTION):
            self.__set_view_mode(_MODE_NO_STRIP)        
            self.__get_vstate().collection_visible = False

        elif (cmd == src.OBS_FULLSCREEN):
            self.__set_view_mode(_MODE_FULLSCREEN)

        elif (cmd == src.OBS_UNFULLSCREEN):
            self.__set_view_mode(_MODE_NORMAL)
            
        #elif (cmd == src.OBS_SHOW_MESSAGE):
        #    msg = args[0]
        #    #self.__ctrlbar.show_message(msg)
            
        #elif (cmd == src.OBS_SHOW_PROGRESS):
        #    value, total = args
        #    #self.__ctrlbar.show_progress("Loading...", value, total)
            
        #elif (cmd == src.OBS_SHOW_PANEL):
        #    pass #self.__ctrlbar.show_panel()

        elif (cmd == src.OBS_STOP_PLAYING):
            issuer = args[0]
            # call all viewers to stop playing
            for v in self.__viewers:
                v.stop_playing(issuer)
                

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
    
        elif (cmd == panel_actions.FORCE_SPEAKER):
            self.__current_viewer.do_toggle_speaker()
            
        elif (cmd == panel_actions.TOGGLE_PLAYLIST):
            self.__current_viewer.do_toggle_playlist()
    
        elif (cmd == panel_actions.SET_POSITION):
            pos = args[0]
            self.__current_viewer.do_set_position(pos)
            
        elif (cmd == panel_actions.TUNE):
            pos = args[0]
            self.__current_viewer.do_tune(pos)


    def __on_observe_strip(self, src, cmd, *args):
    
        handled = False
        if (cmd == src.OBS_SCROLLING):
            # invalidate ticket
            self.__ticket = 0
    
        elif (cmd == src.OBS_CLICKED):
            px, py = args
            if (30 <= py < 420 and px > 108):
                idx = self.__strip.get_index_at(py)            
                self.__select_item(idx)
                handled = True
            elif (0 <= px <= 80 and py >= 420):
                self.__show_tabs()
                handled = True

        return handled
           
    def __on_observe_headset(self, src, cmd, *args):
    
        if (cmd == src.OBS_BUTTON_PRESSED):
            self.__current_viewer.do_enter()
           
           
    def __get_vstate(self):
    
        return self.__viewer_states[self.__current_viewer]
            
            
    def __select_item(self, idx):

        self.__hilight_item(idx)

        item = self.__current_collection[idx]
        self.__get_vstate().selected_item = idx
        self.__current_viewer.load(item)
        self.__strip.scroll_to_item(idx)


    def __hilight_item(self, idx):
    
        # restore saved image
        if (self.__saved_image_index >= 0):
            img = self.__strip.get_image(self.__saved_image_index)
            img.set_hilighted(False)
            #img.draw_pixmap(self.__saved_image, 0, 0)
            #del self.__saved_image
        
        if (idx >= 0):    
            img = self.__strip.get_image(idx)
            img.set_hilighted(True)
            #self.__saved_image = img.clone()
            #img.draw_pixbuf(theme.selection_frame, 0, 0)
        
        self.__saved_image_index = idx
        self.__strip.render()        

            
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

        vstate = self.__get_vstate()
        if (vstate.collection_visible):
            self.__set_view_mode(_MODE_NORMAL)
        else:
            self.__set_view_mode(_MODE_NO_STRIP)
        
        def f():
            self.__root_pane.set_frozen(True)
            viewer.show()
            self.__ctrl_panel.set_capabilities(vstate.caps)
            #self.__title_panel.set_time(0, 0)
            self.__title_panel.set_title(vstate.title)
            self.__title_panel.set_info(vstate.info)
            
            offset = vstate.item_offset
            item_idx = vstate.selected_item
            self.__strip.set_offset(offset)
            if (item_idx >= 0):
                self.__hilight_item(item_idx)

            self.__root_pane.fx_slide_in() #render() #_buffered()
            self.__root_pane.set_frozen(False)

        gobject.idle_add(f)



    def __set_collection(self, collection):
        """
        Loads the given collection into the item strip.
        """

        self.__hilight_item(-1)
        thumbnails = [ item.get_thumbnail() for item in collection ]                
        
        vstate = self.__get_vstate()        
        if (not vstate.thumbs_loaded):
            total = len(thumbnails)
            cnt = 1
            for t in thumbnails:
                if (cnt < 50): t.render()

                #if (cnt % 5 == 0 or (cnt == total and cnt > 5)):
                #    while (gtk.events_pending()): gtk.main_iteration()
                    
                cnt += 1                    
            #end for
        #end if

        self.__strip.set_images(thumbnails)

        if (not vstate.thumbs_loaded):
            vstate.thumbs_loaded = True

        # if the collection is empty, tell the user that she can add items
        if (not collection):
            gobject.idle_add(dialogs.info, "No items found!",
                      "There are no items.\n"
                      "Please go to Media Collection in the Preferences view\n"
                      "to tell MediaBox where to look for your files.")
            

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

