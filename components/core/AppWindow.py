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
from mediabox.Thumbnailer import Thumbnailer
from mediabox.ViewerState import ViewerState
from ui.Image import Image
from ui.Pixmap import Pixmap
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from ui import pixbuftools
from ui import dialogs
from mediabox import config
from mediabox import values
from utils import maemo
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

        # thumbnail screen
        self.__thumbnailer = Thumbnailer()
        self.__thumbnailer.set_visible(False)
        self.__root_pane.add(self.__thumbnailer)

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
        self.__ctrl_panel.set_bg(theme.mb_panel)
        self.__ctrl_panel.set_visible(False)

        #self.__prepare_collection_caps()

        # tab panel and window controls
        self.__tab_panel = TabPanel()
        self.__tab_panel.set_geometry(0, 330, 800, 150)
        self.__tab_panel.set_visible(False)
        self.__tab_panel.add_observer(self.__on_observe_tabs)
        
        self.__window_ctrls = WindowControls()
        self.__window_ctrls.set_geometry(600, 0, 200, 80)
        self.__window_ctrls.set_visible(False)
        self.__window_ctrls.add_observer(self.__on_observe_window_ctrls)

        # search-as-you-type entry
        #def f(src):
        #    src.hide()
        #    self.__set_search_term(src.get_text().lower())

        self.__search_as_you_type_handler = None
        self.__search_as_you_type_entry = gtk.Entry()
        self.__search_as_you_type_entry.modify_font(theme.font_plain)
        self.__search_as_you_type_entry.set_size_request(400, 32)
        self.__window.put(self.__search_as_you_type_entry, 200, 4)
        #self.__search_as_you_type_entry.connect("changed", f)
             
        self.__startup()
        
       
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """
        
        actions = [(self.__root_pane.render_buffered, []),
                   (self.__root_pane.add, [self.__tab_panel]),
                   (self.__root_pane.add, [self.__window_ctrls]),
                   (self.__register_viewers, []),
                   (self.__add_panels, []),
                   (self.__splash.set_visible, [False]),                   
                   (self.__root_pane.render_buffered, []),
                   (self.__scan_media, [True]),
                   (self.__select_viewer, [0]),
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
    
        left_top = pixbuftools.make_frame(theme.mb_panel, 170, 40, True,
                                          pixbuftools.LEFT |
                                          pixbuftools.BOTTOM)
        left_bottom = pixbuftools.make_frame(theme.mb_panel, 170, 70, True,
                                          pixbuftools.TOP |
                                          pixbuftools.LEFT)
        pixbuftools.draw_pbuf(left_bottom, theme.mb_btn_turn_1, 30, 15)

        self.__title_panel_left.set_image(left_top)
        self.__panel_left.set_image(left_bottom)
        self.__strip.set_caps(left_top, left_bottom)


    def __on_click_title(self):
        """
        Reacts on clicking the title panel.
        """

        self.__show_search_entry()
        

                 
    def __on_menu_button(self, px, py):
        """
        Reacts on pressing the menu button.
        """
        
        self.__show_tabs()


    def __show_tabs(self):
    
        self.__hide_search_entry()

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
            dialogs.warning("No media library specified!",
                            "Please specify the contents of your\n"
                            "media library in the folder viewer.")
            return
        #end if


        view_mode = self.__view_mode
        self.__set_view_mode(viewmodes.TITLE_ONLY)
        if (self.__current_viewer):
            self.__current_viewer.set_visible(False)
        self.__thumbnailer.clear()        
        self.__thumbnailer.set_visible(True)
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
        self.__thumbnailer.set_visible(False)
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
            self.__kscr.impulse(0, 7.075)
        elif (key == "Down"):
            self.__kscr.impulse(0, -7.075)
            
        elif (key == "XF86Headset"):
            #self.__current_viewer.do_enter()
            self.emit_event(msgs.HWKEY_EV_HEADSET)
            
        
        elif (key == "BackSpace"):
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


    def __show_search_entry(self):
        """
        Displays the search entry box.
        """

        def check_text():
            text = "" #self.__search_as_you_type_entry.get_text().lower()
            if (text != self.__get_search_term()):
                self.__set_search_term(text)
            return True

        self.__search_as_you_type_entry.set_text("Search")
        self.__search_as_you_type_entry.select_region(0, -1)
        self.__search_as_you_type_entry.show()
        
        if (not self.__search_as_you_type_handler):
            self.__search_as_you_type_handler = \
                gobject.timeout_add(300, check_text)
    
        self.__reset_search_timeout()
        
        
    def __hide_search_entry(self):
        """
        Hides the search entry box.
        """

        self.__search_as_you_type_entry.hide()
        self.__search_as_you_type_entry.set_text("")

        if (self.__search_as_you_type_handler):
            gobject.source_remove(self.__search_as_you_type_handler)
            self.__search_as_you_type_handler = None


    def __reset_search_timeout(self):
        """
        Resets the timeout after which the search gets cleared.
        """

        def f():
            self.__hide_search_entry()
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
    
        if (event == msgs.CORE_ACT_SCAN_MEDIA):
            force = args[0]
            self.__scan_media(force)

        #elif (event == msgs.MEDIASCANNER_EV_THUMBNAIL_GENERATED):
        #    thumburi, f = args
        #    name = os.path.basename(f.name)
        #    self.__title_panel.set_title(name)
        #    self.__thumbnailer.show_thumbnail(thumburi, name)
    
        #elif (event == msgs.CORE_EV_DEVICE_ADDED):
        #    ident, dev = args
        #    gobject.timeout_add(0, self.__scan_media, True)
        
        #elif (event == msgs.CORE_ACT_SHOW_MENU):
        #    self.__show_tabs()
        #    self.drop_event()
        
        elif (event == msgs.CORE_EV_THEME_CHANGED):
            self.__root_pane.propagate_theme_change()
            self.__prepare_collection_caps()
            #self.__root_pane.render_buffered()
            self.__root_pane.fx_fade_in()
    
        elif (event == msgs.CORE_ACT_RENDER_ALL):
            self.__root_pane.render_buffered()
            #self.__root_pane.render()
            self.drop_event()

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
            
        elif (event == msgs.CORE_ACT_RENDER_ITEMS):
            self.__strip.invalidate_buffer()
            self.__strip.render()

        elif (event == msgs.CORE_ACT_SET_TOOLBAR):
            tbset = args[0]
            self.__ctrl_panel.set_toolbar(tbset)

        elif (event == msgs.MEDIA_EV_VOLUME_CHANGED):
            percent = args[0]
            self.__title_panel.set_volume(percent)
            
         
    def __get_vstate(self, viewer = None):
    
        if (not viewer):
            viewer = self.__current_viewer
        return self.__viewer_states[viewer]
                
            
            
    def __select_item(self, idx):

        self.__hilight_item(idx)

        #item = self.__current_collection[idx]
        self.__get_vstate().selected_item = idx
        #self.__current_viewer.load(item)
        self.emit_event(msgs.CORE_ACT_LOAD_ITEM, idx)
        self.__strip.scroll_to_item(idx)


    def __hilight_item(self, idx):
    
        # restore saved image
        if (self.__saved_image_index >= 0):
            img = self.__strip.get_image(self.__saved_image_index)
            img.set_hilighted(False)
            #img.draw_pixmap(self.__saved_image, 0, 0)
            #del self.__saved_image
            self.__strip.invalidate_buffer()
        
        if (idx >= 0):    
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
        self.__strip.render()

        # if the collection is empty, tell the user that she can add items
        #if (not collection):
        #    gobject.idle_add(dialogs.info, "No items found!",
        #              "There are no items.\n"
        #              "Please go to Media Collection in the Preferences view\n"
        #              "to tell MediaBox where to look for your files.")

        
        
    def __try_quit(self):
    
        result = dialogs.question("Exit", "Really quit?")
        if (result == 0):
            self.emit_event(msgs.CORE_EV_APP_SHUTDOWN)
            gtk.main_quit()

