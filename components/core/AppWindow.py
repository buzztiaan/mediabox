from com import Component, Viewer, msgs
import components
from utils import logging

from mediabox.MainWindow import MainWindow
from mediabox.SplashScreen import SplashScreen
from mediabox.RootPane import RootPane
from mediabox.TitlePanel import TitlePanel
from mediabox.ControlPanel import ControlPanel
from mediabox.TabPanel import TabPanel
from mediabox.WindowControls import WindowControls
from mediabox.ViewerState import ViewerState
from ui.Image import Image
from ui.Pixmap import Pixmap
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from ui.EventBox import EventBox
from ui import pixbuftools
from ui import dialogs
from mediabox import config
from mediabox import values
from utils import maemo
from utils import hildon_input_method
from mediabox import viewmodes
import theme

import gtk
import gobject
import os
import time



class AppWindow(Component):
    """
    Main class of the application.
    """

    def __init__(self):

        self.__viewers = []
        self.__current_viewer = None
        self.__current_collection = []
        self.__current_mediaroots = []
        self.__view_mode = viewmodes.TITLE_ONLY
        self.__battery_remaining = 100.0
        
        # mapping: viewer -> state
        self.__viewer_states = {}

        self.__saved_image = None
        self.__saved_image_index = -1
        
        # flag for indicating whether media scanning has already been scheduled
        self.__media_scan_scheduled = False
    
        # search string for finding items with the keyboard
        self.__keyboard_search_string = ""
        # timer for clearing the search term
        self.__keyboard_search_reset_timer = None

        self.__hildon_input_replace = True
        
        # flag for indicating whether initialization has finished
        self.__is_initialized = False
    
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

        Component.__init__(self)

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
        RootPane.set_event_sensor(self.__window)
        self.__root_pane = RootPane()
        self.__root_pane.set_screen(self.__screen)

        # splash screen
        self.__splash = SplashScreen()
        self.__splash.set_visible(True)
        self.__root_pane.add(self.__splash)

        # image strip       
        self.__strip = ImageStrip(5)
        self.__strip.set_geometry(0, 0, 170, 480)
        #self.__strip.set_caps(left_top, left_bottom)
        self.__strip.set_bg_color(theme.color_bg)
        self.__strip.set_visible(False)
        self.__root_pane.add(self.__strip)

        self.__kscr = KineticScroller(self.__strip)
        self.__kscr.set_touch_area(0, 108)
        self.__kscr.add_observer(self.__on_observe_strip)

        # title panel
        self.__title_panel_left = Image(None)
        self.__title_panel_left.set_geometry(0, 0, 170, 40)
        self.__title_panel_left.set_visible(False)
        
        self.__title_panel = TitlePanel()
        self.__title_panel.set_geometry(170, 0, 630, 40)
        self.__title_panel.set_title("Initializing")
        self.__title_panel.set_visible(False)
        self.__title_panel.connect_clicked(self.__on_click_title)
       
        # control panel
        self.__panel_left = Image(None)
        self.__panel_left.set_geometry(0, 410, 160, 70)
        self.__panel_left.connect_button_pressed(self.__on_menu_button)
        self.__panel_left.set_visible(False)
        
        self.__ctrl_panel = ControlPanel()
        self.__ctrl_panel.set_geometry(170, 410, 630, 70)
        self.__ctrl_panel.set_visible(False)

        # tab panel and window controls
        self.__tab_panel = TabPanel()
        self.__tab_panel.set_geometry(0, 330, 800, 150)
        self.__tab_panel.set_visible(False)
        self.__tab_panel.add_observer(self.__on_observe_tabs)
        
        self.__window_ctrls = WindowControls()
        self.__window_ctrls.set_geometry(600, 0, 200, 80)
        self.__window_ctrls.set_visible(False)
        self.__window_ctrls.add_observer(self.__on_observe_window_ctrls)

        self.__touch_back_area = EventBox()
        self.__touch_back_area.connect_button_pressed(
                                          lambda x,y:self.__tab_panel.close())
        self.__touch_back_area.set_visible(False)
        self.__root_pane.add(self.__touch_back_area)

        self.__startup()
        
       
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """

        actions = [(self.__root_pane.render_buffered, []),
                   (self.__splash.set_text, ["Loading Components..."]),
                   #(gtk.main_quit, []),
                   #(time.sleep, [10]),
                   (self.__register_viewers, []),
                   (self.__splash.set_text, ["Scanning Media Library..."]),
                   (self.__scan_media, [True]),
                   (self.__splash.set_visible, [False]),
                   (self.__root_pane.render_buffered, []),
                   (self.__root_pane.add, [self.__tab_panel]),
                   (self.__root_pane.add, [self.__window_ctrls]),
                   (self.__add_panels, []),
                   (self.__select_initial_viewer, []),
                   ]
                   
        def f():
            if (actions):                
                act, args = actions.pop(0)
                logging.debug("running startup action %s, %s", `act`, `args`)
                try:
                    act(*args)
                except:
                    import traceback; traceback.print_exc()
                    pass
                return True
            else:
                logging.debug("startup complete")
                return False
                
        gobject.idle_add(f)


    def __select_initial_viewer(self):
        """
        Selects the viewer that is initially shown. Shows the menu if no
        viewer was set.
        """
        
        self.__is_initialized = True
        current_viewer = config.current_viewer()
        viewers = [ v for v in self.__viewers if repr(v) == current_viewer ]
        if (viewers):
            v = viewers[0]
            idx = self.__viewers.index(v)
            self.__select_viewer(idx)
            self.__tab_panel.select_viewer(idx)
        else:
            self.__show_tabs()


    def __register_viewers(self):
        """
        Sorts and registers the viewers.
        """

        self.__viewers.sort(lambda a,b:cmp(a.PRIORITY, b.PRIORITY))

        for viewer in self.__viewers:
            self.__tab_panel.add_viewer(viewer)
            self.__root_pane.add(viewer)
            viewer.set_visible(False)        
            vstate = ViewerState()
            self.__viewer_states[viewer] = vstate


    def __add_panels(self):
        """
        Adds the panel components.
        """
    
        self.__root_pane.add(self.__title_panel_left)
        self.__root_pane.add(self.__title_panel)
        self.__root_pane.add(self.__panel_left)
        self.__root_pane.add(self.__ctrl_panel)
        self.__prepare_collection_caps()
        
        
    def __set_view_mode(self, view_mode):
        """
        Sets the view mode.
        """

        if (not self.__is_initialized): return

        if (view_mode == viewmodes.NORMAL):
            self.__title_panel_left.set_visible(False)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(True)
            self.__strip.set_visible(True)
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(180, 40, 620, 370)
                self.__get_vstate().collection_visible = True
            
        elif (view_mode == viewmodes.NO_STRIP):
            self.__title_panel_left.set_visible(True)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(True)
            self.__ctrl_panel.set_visible(True)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 40, 800, 370)
                self.__get_vstate().collection_visible = False

        elif (view_mode == viewmodes.NO_STRIP_PANEL):
            self.__title_panel_left.set_visible(False)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(True)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 0, 800, 480)
                self.__get_vstate().collection_visible = False
            
        elif (view_mode == viewmodes.FULLSCREEN):
            self.__title_panel_left.set_visible(False)
            self.__title_panel.set_visible(False)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(False)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 0, 800, 480)

        elif (view_mode == viewmodes.TITLE_ONLY):
            self.__title_panel_left.set_visible(True)
            self.__title_panel.set_visible(True)
            self.__panel_left.set_visible(False)
            self.__ctrl_panel.set_visible(False)
            self.__strip.set_visible(False)
            if (self.__current_viewer):            
                self.__current_viewer.set_geometry(0, 40, 800, 440)
                self.__get_vstate().collection_visible = False

        self.__view_mode = view_mode



    def __prepare_collection_caps(self):
    
        repeat_mode = config.repeat_mode()
        shuffle_mode = config.shuffle_mode()
    
        left_top = pixbuftools.make_frame(theme.mb_panel, 170, 40, True,
                                          pixbuftools.LEFT |
                                          pixbuftools.BOTTOM)
        left_bottom = pixbuftools.make_frame(theme.mb_panel, 170, 70, True,
                                          pixbuftools.TOP |
                                          pixbuftools.LEFT)

        if (repeat_mode == config.REPEAT_MODE_ONE):
            icon = theme.mb_status_repeat_one
        elif (repeat_mode == config.REPEAT_MODE_ALL):
            icon = theme.mb_status_repeat_none
        else:
            icon = theme.mb_status_repeat_none
        pixbuftools.draw_pbuf(left_top, icon, 50, 4)
        
        if (shuffle_mode == config.SHUFFLE_MODE_ONE):
            icon = theme.mb_status_shuffle_one
        elif (shuffle_mode == config.SHUFFLE_MODE_ALL):
            icon = theme.mb_status_shuffle_none
        else:
            icon = theme.mb_status_shuffle_none
        pixbuftools.draw_pbuf(left_top, icon, 90, 4)

        br = self.__battery_remaining
        if (br > 80.0):
            icon = theme.mb_status_battery_4
        elif (br > 60.0):
            icon = theme.mb_status_battery_3
        elif (br > 40.0):
            icon = theme.mb_status_battery_2
        elif (br > 20.0):
            icon = theme.mb_status_battery_1
        else:
            icon = theme.mb_status_battery_0
        pixbuftools.draw_pbuf(left_top, icon, 10, 4)

        pixbuftools.draw_pbuf(left_bottom, theme.mb_btn_turn_1, 30, 15)

        

        self.__title_panel_left.set_image(left_top)
        self.__panel_left.set_image(left_bottom)
        self.__strip.set_caps(left_top, left_bottom)


    def __on_click_title(self):
        """
        Reacts on clicking the title panel.
        """

        self.__show_virtual_keyboard()
        

                 
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
        
        self.__touch_back_area.set_visible(True)
        self.__touch_back_area.set_enabled(True)
        w, h = self.__root_pane.get_size()
        tw, th = self.__tab_panel.get_size()
        cw, ch = self.__window_ctrls.get_size()
        self.__touch_back_area.set_geometry(0, 0, w - cw, h - th)



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
            dialogs.warning("No media library specified!",
                            "Please specify the contents of your\n"
                            "media library in the folder viewer.")
            return
        #end if


        view_mode = self.__view_mode
        self.__set_view_mode(viewmodes.TITLE_ONLY)
        if (self.__current_viewer):
            self.__current_viewer.set_visible(False)
        self.__root_pane.render_buffered()
        #while (gtk.events_pending()): gtk.main_iteration()


        paths = []
        for path, mtypes in mediaroots:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f): paths.append((f, mtypes))
        #end for
        self.emit_event(msgs.MEDIASCANNER_ACT_SCAN, paths)
        

        #while (gtk.events_pending()): gtk.main_iteration()

        for v in self.__viewers:
            self.__viewer_states[v].selected_item = -1
            self.__viewer_states[v].item_offset = 0

        self.__set_view_mode(view_mode)

        if (self.__current_viewer):
            self.__current_viewer.set_visible(True)        
        self.__root_pane.render_buffered()

        import gc; gc.collect()

                        
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
        logging.debug("current Resident Set Size: %0.02f MB", size)
                
    
        if (not self.__root_pane.is_enabled()): return
    
        keyval = ev.keyval
        key = gtk.gdk.keyval_name(keyval)

        logging.debug("key pressed: [%s]", key)
        
        if (key == "space"): key = " "
        
        if (key == "Escape"):
            self.__try_quit()
        elif (key == "Return"):
            self.emit_event(msgs.HWKEY_EV_ENTER)
        elif (key == "F6"):            
            self.emit_event(msgs.HWKEY_EV_FULLSCREEN)
        elif (key == "F7"):
            self.emit_event(msgs.HWKEY_EV_INCREMENT)
        elif (key == "F8"):
            self.emit_event(msgs.HWKEY_EV_DECREMENT)
            
        elif (key == "Up"):
            self.emit_event(msgs.HWKEY_EV_UP)
            #self.__kscr.impulse(0, 7.075)
        elif (key == "Down"):
            self.emit_event(msgs.HWKEY_EV_DOWN)
            #self.__kscr.impulse(0, -7.075)
            
        elif (key == "XF86Headset"):
            #self.__current_viewer.do_enter()
            self.emit_event(msgs.HWKEY_EV_HEADSET)
            
        
        elif (key == "BackSpace"):
            print "BACKSPACE"
            term = self.__get_search_term()
            if (term):
                term = term[:-1]
                self.__set_search_term(term)
        
        elif (len(key) == 1 and ord(key) > 31):
            print "KEY", key

            term = self.__get_search_term()
            term += key.lower()
            self.__set_search_term(term)
        
        else:
            pass
            
        return True


    def __show_virtual_keyboard(self):
        """
        Displays the virtual keyboard.
        """

        def f(src, s):            
            print src, s
            if (not s):
                self.__hildon_input_replace = False
                return
                
            term = self.__get_search_term()
            if (self.__hildon_input_replace):
                term = ""
            else:
                term = self.__get_search_term()
            self.__hildon_input_replace = True
    
            term += s.lower()
            self.__set_search_term(term)

        try:
            hildon_input_method.show_im(self.__window, f)
        except:
            # only available on maemo
            pass
        self.__set_search_term("")



    def __reset_search_timeout(self):
        """
        Resets the timeout after which the search gets cleared.
        """

        def f():
            self.__keyboard_search_string = ""
            self.__keyboard_search_reset_timer = None

        if (self.__keyboard_search_reset_timer):
            gobject.source_remove(self.__keyboard_search_reset_timer)
        self.__keyboard_search_reset_timer = gobject.timeout_add(2000, f)



    def __get_search_term(self):
        """
        Returns the current search term.
        """
    
        return self.__keyboard_search_string


    def __set_search_term(self, term):
        """
        Sets the search term to the given value.
        """
        
        self.__keyboard_search_string = term

        #if (not term): return
        
        self.__title_panel.set_title_with_timeout("Search: " + term, 2000)
        self.__reset_search_timeout()
        
        if (term):
            self.emit_event(msgs.CORE_ACT_SEARCH_ITEM, term)
        
        

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
            self.__touch_back_area.set_visible(False)

            if (self.__viewers[idx] != self.__current_viewer):
                #self.__root_pane.fx_fade_out()
                self.__root_pane.set_enabled(True)
                self.__root_pane.set_frozen(False)
                self.__select_viewer(idx)
            else:
                self.__tab_panel.fx_lower()
                self.__root_pane.set_enabled(True)
                self.__root_pane.set_frozen(False)
                self.__root_pane.render_buffered()
        
        elif (cmd == src.OBS_REPEAT_MODE):
            mode = args[0]
            config.set_repeat_mode(mode)
            self.__prepare_collection_caps()
            
        elif (cmd == src.OBS_SHUFFLE_MODE):
            mode = args[0]
            config.set_shuffle_mode(mode)
            self.__prepare_collection_caps()

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


    def handle_event(self, event, *args):

        if (event == msgs.COM_EV_COMPONENT_LOADED):
            component = args[0]
            if (isinstance(component, Viewer)):
                self.__viewers.append(component)
    
        elif (event == msgs.CORE_ACT_SCAN_MEDIA):
            force = args[0]
            self.__scan_media(force)
   
        #elif (event == msgs.CORE_EV_DEVICE_ADDED):
        #    ident, dev = args
        #    gobject.timeout_add(0, self.__scan_media, True)
        
        #elif (event == msgs.CORE_ACT_SHOW_MENU):
        #    self.__show_tabs()
        #    self.drop_event()
        
        elif (event == msgs.CORE_EV_THEME_CHANGED):
            self.__root_pane.set_frozen(True)
            self.__root_pane.propagate_theme_change()
            self.__prepare_collection_caps()
            #self.__root_pane.render_buffered()            
            self.__root_pane.fx_slide_in()
    
    
        elif (event == msgs.UI_ACT_FREEZE):
            self.__root_pane.set_frozen(True)
            
        elif (event == msgs.UI_ACT_THAW):
            self.__root_pane.set_frozen(False)
            self.__root_pane.render_buffered()
            
        elif (event == msgs.UI_ACT_RENDER):
            self.__root_pane.render_buffered()
            

        elif (event == msgs.CORE_ACT_VIEW_MODE):
            mode = args[0]
            self.__set_view_mode(mode)
            self.drop_event()

   
        elif (event == msgs.SYSTEM_EV_DRIVE_MOUNTED):
            def f():
                self.__scan_media(True)
                self.__media_scan_scheduled = False

            if (not self.__media_scan_scheduled):
                self.__media_scan_scheduled = True
                gobject.timeout_add(500, f)
                
        elif (event == msgs.SYSTEM_EV_BATTERY_REMAINING):
            percent = args[0]
            self.__battery_remaining = percent
            self.__prepare_collection_caps()


        elif (event == msgs.CORE_ACT_SET_TITLE):
            title = args[0]
            self.__title_panel.set_title(title)

        elif (event == msgs.CORE_ACT_SET_INFO):
            info = args[0]
            self.__title_panel.set_info(info)

        elif (event == msgs.CORE_ACT_SET_COLLECTION):
            items = args[0]
            self.__current_collection = items
            self.__set_collection(items)

            self.__saved_image = None
            self.__saved_image_index = -1
           
        elif (event == msgs.CORE_ACT_SELECT_ITEM):
            idx = args[0]
            self.__select_item(idx)
            
        elif (event == msgs.CORE_ACT_HILIGHT_ITEM):
            idx = args[0]
            self.__select_item(idx, hilight_only = True)
            
        elif (event == msgs.CORE_ACT_SCROLL_TO_ITEM):
            idx = args[0]
            self.__strip.scroll_to_item(idx)
            
        elif (event == msgs.CORE_ACT_RENDER_ITEMS):
            self.__strip.invalidate_buffer()
            self.__strip.render()

        elif (event == msgs.CORE_ACT_SET_TOOLBAR):
            tbset = args[0]
            self.__ctrl_panel.set_toolbar(tbset)

        elif (event == msgs.MEDIA_EV_VOLUME_CHANGED):
            percent = args[0]
            self.__title_panel.set_volume(percent)
            
        elif (event == msgs.MEDIA_EV_LOADED):
            viewer, f = args
            idx = self.__viewers.index(viewer)
            self.__tab_panel.set_currently_playing(idx)
         
    def __get_vstate(self, viewer = None):
    
        if (not viewer):
            viewer = self.__current_viewer
        return self.__viewer_states[viewer]
                
            
            
    def __select_item(self, idx, hilight_only = False):

        self.__hilight_item(idx)

        if (not hilight_only):
            #item = self.__current_collection[idx]
            self.__get_vstate().selected_item = idx
            #self.__current_viewer.load(item)
            self.emit_event(msgs.CORE_ACT_LOAD_ITEM, idx)
            
        self.__strip.scroll_to_item(idx)


    def __hilight_item(self, idx):
    
        # restore saved image
        if (self.__saved_image_index >= 0 and
              self.__saved_image_index < len(self.__strip.get_images())):
            img = self.__strip.get_image(self.__saved_image_index)
            img.set_hilighted(False)
            #img.draw_pixmap(self.__saved_image, 0, 0)
            #del self.__saved_image
            self.__strip.invalidate_buffer()
        
        if (idx >= 0 and idx < len(self.__strip.get_images())):
            img = self.__strip.get_image(idx)
            img.set_hilighted(True)
            #self.__saved_image = img.clone()
            #img.draw_pixbuf(theme.selection_frame, 0, 0)
            self.__strip.invalidate_buffer()
        
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
            self.__set_view_mode(viewmodes.NORMAL)
        else:
            self.__set_view_mode(viewmodes.NO_STRIP)
        
        def f():
            self.__scan_media(False)
            self.__root_pane.set_frozen(True)
            viewer.show()
            #self.__title_panel.set_time(0, 0)
            #self.__title_panel.set_title(vstate.title)
            #self.__title_panel.set_info(vstate.info)
            
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
        thumbnails = collection #[ item.thumbnail_pmap for item in collection ]
        
        self.__strip.set_images(thumbnails)
        #self.__strip.invalidate_buffer()
        #self.__strip.render()

        # if the collection is empty, tell the user that she can add items
        #if (not collection and self.__view_mode == viewmodes.NORMAL):
        #    gobject.idle_add(dialogs.info, "No items found!",
        #              "There are no items.\n"
        #              "Please go to Media Collection in the Preferences view\n"
        #              "to tell MediaBox where to look for your files.")

        
        
    def __try_quit(self):
    
        result = dialogs.question("Exit", "Really quit?")
        if (result == 0):
            config.set_current_viewer(self.__current_viewer)
            self.emit_event(msgs.CORE_EV_APP_SHUTDOWN)
            gtk.main_quit()

