from com import Component, Viewer, Widget, msgs
import components
from utils import logging

from MainWindow import MainWindow
from RootPane import RootPane
from TitlePanel import TitlePanel
from ControlPanel import ControlPanel
from ViewerState import ViewerState
from ui.Button import Button
from ui.Pixmap import Pixmap
from ui.Widget import Widget as UIWidget
from mediabox import config
from mediabox import values
from utils import maemo
from mediabox import viewmodes
from theme import theme

import gtk
import gobject
import os
import time


# interval for hw key autorepeater in ms
_AUTOREPEATER_INTERVAL = 200


class AppWindow(Component, RootPane):
    """
    Main window of the application.
    """

    def __init__(self):

        self.__viewers = []
        self.__current_viewer = None
        self.__current_device_id = ""
        self.__view_mode = viewmodes.TITLE_ONLY
        self.__battery_remaining = 100.0
        
        # auto repeat handler for hw keys without auto repeat
        self.__autorepeater = None
        
        self.__is_fullscreen = True
        
        # mapping: viewer -> state
        self.__viewer_states = {}

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
    

        # window
        self.__window = MainWindow()
        self.__window.set_app_paintable(True)
        self.__window.connect("delete-event", self.__on_close_window)
        self.__window.connect("expose-event", self.__on_expose)
        self.__window.connect("key-press-event", self.__on_key)
        self.__window.connect("key-release-event", lambda *a:self.__autorepeat_stop())
        self.__window.connect("configure-event", self.__on_resize_window)
        self.__window.set_title("%s %s" % (values.NAME, values.VERSION))
        self.__window.show()
        w, h = self.__window.get_size()

        if (maemo.IS_MAEMO):
            self.__program.add_window(self.__window)

        # screen pixmap
        screen = Pixmap(self.__window.window)
        
        Component.__init__(self)
        RootPane.__init__(self)
        self.set_window(self.__window)
        self.set_size(w, h)
        self.set_screen(screen)

        self.__box = UIWidget()
        self.add(self.__box)
        self.push_actor(self.__box)
        

        # image strip
        self.__btn_strip = Button(">")
        self.__btn_strip.set_visible(False)
        self.__btn_strip.connect_clicked(self.__on_show_side_strip)
        self.__box.add(self.__btn_strip)
        
        #self.__strip = ImageStrip(5)
        #self.__strip.set_bg_color(theme.color_mb_background)
        #self.__strip.set_visible(False)
        #self.add(self.__strip)
        
        #self.__kscr = KineticScroller(self.__strip)
        #self.__kscr.set_touch_area(0, 108)
        #self.__kscr.add_observer(self.__on_observe_strip)

        # title panel
        self.__title_panel = TitlePanel()
        self.__title_panel.set_title("Initializing")
        self.__title_panel.set_visible(False)
        self.__title_panel.connect_clicked(self.__on_click_title)
       
        # control panel
        self.__ctrl_panel = ControlPanel()
        self.__ctrl_panel.set_visible(False)
        self.__ctrl_panel.connect_button_pressed(self.__on_menu_button)

        gobject.timeout_add(0, self.__startup)

        
       
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """

        actions = [#(self.render_buffered, []),
                   #(gtk.main_quit, []),
                   (self.show_overlay, ["%s %s" % (values.NAME, values.VERSION),
                                        "",
                                        theme.mb_viewer_audio]),
                   #(time.sleep, [5]),
                   (self.__register_viewers, []),
                   #(self.show_overlay, ["%s %s" % (values.NAME, values.VERSION),
                   #                     "- starting -",
                   #                     theme.mb_viewer_audio]),
                   (self.__add_panels, []),
                   (self.__scan_at_startup, []),
                   (self.hide_overlay, []),
                   (self.__select_initial_viewer, []),
                   (self.emit_message, [msgs.CORE_EV_APP_STARTED]),
                   ]
                   
        def f():
            if (actions):                
                act, args = actions.pop(0)
                logging.info("running startup action %s, %s", `act`, `args`)
                try:
                    act(*args)
                except:
                    import traceback; traceback.print_exc()
                    pass
                return True
            else:
                logging.info("startup complete, took %0.2f seconds" \
                              % (time.time() - values.START_TIME))
                return False
                
        for act, args in actions:
            logging.info("running startup action %s, %s", `act`, `args`)
            try:
                act(*args)
            except:
                logging.error("an error occured:\n%s", logging.stacktrace())
        #end for
        
        logging.info("startup complete, took %0.2f seconds" \
                        % (time.time() - values.START_TIME))

        #gobject.timeout_add(0, f)



    def __scan_at_startup(self):
        """
        Scans the media at startup if the user wants it so.
        """
    
        if (config.scan_at_startup()):
            self.__scan_media(True)
        else:
            #self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)
            self.__scan_media(False)



    def __select_initial_viewer(self):
        """
        Selects the viewer that is initially shown. Shows the menu if no
        viewer was set.
        """
        
        self.__is_initialized = True
        current_viewer = config.current_viewer()
        current_device_id = config.current_device()
        self.__select_viewer_by_name(current_viewer)
        self.emit_message(msgs.UI_ACT_SELECT_VIEWER, current_viewer)
        #self.emit_message(msgs.UI_ACT_SELECT_DEVICE, current_device_id)


    def __register_viewers(self):
        """
        Sorts and registers the viewers.
        """

        self.__viewers.sort(lambda a,b:cmp(a.PRIORITY, b.PRIORITY))

        for viewer in self.__viewers:
            logging.info("registering viewer [%s]", viewer)
            self.__box.add(viewer)
            viewer.set_visible(False)


    def __add_panels(self):
        """
        Adds the panel components.
        """
    
        self.__box.add(self.__title_panel)
        self.__box.add(self.__ctrl_panel)


    def render_this(self):
    
        RootPane.render_this(self)
    
        w, h = self.get_size()
        screen = self.get_screen()

        self.__title_panel.set_geometry(0, 0, w, 40)
        self.__ctrl_panel.set_geometry(0, h - 70, w, 70)
        #self.__strip.set_geometry(0, 0, 170, h)
        self.__btn_strip.set_geometry(0, 40, 64, h - 110)

        
        if (self.__view_mode == viewmodes.NORMAL):
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(64, 40, w - 64, h - 110)

        elif (self.__view_mode == viewmodes.NO_STRIP):
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(0, 40, w, h - 110)

        elif (self.__view_mode == viewmodes.NO_STRIP_PANEL):
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(0, 0, w, h)
            
        elif (self.__view_mode == viewmodes.FULLSCREEN):
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(0, 0, w, h)

        elif (self.__view_mode == viewmodes.TITLE_ONLY):
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(0, 40, w, h - 40)
        
        
    def __set_view_mode(self, view_mode):
        """
        Sets the view mode.
        """

        if (not self.__is_initialized): return
        if (view_mode == self.__view_mode): return

        w, h = self.get_size()

        if (view_mode == viewmodes.NORMAL):
            self.__title_panel.set_visible(True)
            self.__ctrl_panel.set_visible(True)
            self.__btn_strip.set_visible(True)
            #if (self.__current_viewer):
            #    self.__get_vstate().view_mode = view_mode
                #self.__current_viewer.set_geometry(64, 40, w - 64, h - 110)
                #self.__get_vstate().collection_visible = True
            
        elif (view_mode == viewmodes.NO_STRIP):
            self.__title_panel.set_visible(True)
            self.__ctrl_panel.set_visible(True)
            self.__btn_strip.set_visible(False)
            #if (self.__current_viewer):
            #    self.__get_vstate().view_mode = view_mode
                #self.__current_viewer.set_geometry(0, 40, w, h - 110)
                #self.__get_vstate().collection_visible = False

        #elif (view_mode == viewmodes.NO_STRIP_PANEL):
        #    self.__title_panel.set_visible(True)
        #    self.__ctrl_panel.set_visible(True)
        #    self.__btn_strip.set_visible(False)
        #    if (self.__current_viewer):            
        #        self.__current_viewer.set_geometry(0, 0, w, h)
        #        self.__get_vstate().collection_visible = False
            
        elif (view_mode == viewmodes.FULLSCREEN):
            self.__title_panel.set_visible(False)
            self.__ctrl_panel.set_visible(False)
            self.__btn_strip.set_visible(False)
            if (self.__current_viewer):
                self.__current_viewer.set_geometry(0, 0, w, h)

        #elif (view_mode == viewmodes.TITLE_ONLY):
        #    self.__title_panel.set_visible(True)
        #    self.__ctrl_panel.set_visible(False)
        #    self.__btn_strip.set_visible(False)
        #    if (self.__current_viewer):            
        #        self.__current_viewer.set_geometry(0, 40, w, h - 40)
        #        self.__get_vstate().collection_visible = False

        self.__view_mode = view_mode
        if (self.__current_viewer):
            self.__get_vstate().view_mode = view_mode


    def __on_click_title(self):
        """
        Reacts on clicking the title panel.
        """

        self.__show_virtual_keyboard()
        

                 
    def __on_menu_button(self, px, py):
        """
        Reacts on pressing the menu button.
        """
        
        #self.__show_tabs()
        if (px < 80):
            self.emit_message(msgs.INPUT_EV_MENU)



    def __scan_media(self, force_rebuild):
        """
        Scans the media root locations for media files.
        
        @param force_scan: scan even if mediaroots and types haven't changed
        """
        
        mediaroots = config.mediaroot()        
    
        if (not mediaroots):
        #    dialogs.warning("No media library specified!",
        #                    "Please specify the contents of your\n"
        #                    "media library in the folder viewer.")
            return
        #end if


        #self.show_overlay("Scanning Media", "", theme.mb_viewer_audio)

        self.emit_message(msgs.MEDIASCANNER_ACT_SCAN, mediaroots, force_rebuild)
        

        for v in self.__viewers:
            vstate = self.__get_vstate(v)
            vstate.selected_item = -1
            vstate.item_offset = 0


        import gc; gc.collect()
        #self.hide_overlay()


    def __on_show_side_strip(self):
        
        self.emit_message(msgs.UI_ACT_SHOW_STRIP)

                        
    def __on_close_window(self, src, ev):
    
        self.__try_quit()
        return True
        
        
    def __on_resize_window(self, src, ev):
            
        w, h = src.get_size()
        if (src.get_size() != self.get_size()):
            logging.debug("resizing window to (%d, %d)" % (w, h))
            screen = Pixmap(self.__window.window)
            self.set_screen(screen)
            self.set_size(w, h)
            self.render_buffered()

    def __on_expose(self, src, ev):
    
        x, y, w, h = ev.area
        screen = self.get_screen()
        screen.restore(x, y, w, h)


    def __autorepeat_start(self, key_msg):
    
        def f():
            self.emit_message(key_msg)
            return True
            
        if (self.__autorepeater):
            gobject.source_remove(self.__autorepeater)
        self.__autorepeater = gobject.timeout_add(_AUTOREPEATER_INTERVAL, f)
        
        
    def __autorepeat_stop(self):

        if (self.__autorepeater):
            gobject.source_remove(self.__autorepeater)
            self.__autorepeater = None    
    

    def __on_key(self, src, ev):
   
        keyval = ev.keyval
        key = gtk.gdk.keyval_name(keyval)

        logging.debug("key pressed: [%s]", key)
        
        if (key == "space"): key = " "
        
        if (key == "Escape"):
            print "Escape"
            self.emit_message(msgs.HWKEY_EV_ESCAPE)
        
        elif (key == "Return"):
            self.emit_message(msgs.HWKEY_EV_ENTER)

        elif (key == "F1"):
            self.emit_message(msgs.HWKEY_EV_F1)
        elif (key == "F2"):
            self.emit_message(msgs.HWKEY_EV_F2)
        elif (key == "F3"):
            self.emit_message(msgs.HWKEY_EV_F3)
        elif (key == "F4"):
            self.emit_message(msgs.HWKEY_EV_F4)
        elif (key == "F5"):
            self.emit_message(msgs.HWKEY_EV_F5)
        elif (key == "F6"):
            self.emit_message(msgs.HWKEY_EV_F6)
            self.emit_message(msgs.HWKEY_EV_FULLSCREEN)  # deprecated
        elif (key == "F7"):
            self.__autorepeat_start(msgs.HWKEY_EV_F7)
            self.emit_message(msgs.HWKEY_EV_F7)
            self.emit_message(msgs.HWKEY_EV_INCREMENT)  # deprecated
        elif (key == "F8"):
            self.__autorepeat_start(msgs.HWKEY_EV_F8)
            self.emit_message(msgs.HWKEY_EV_F8)
            self.emit_message(msgs.HWKEY_EV_DECREMENT)  # deprecated
        elif (key == "F9"):
            self.emit_message(msgs.HWKEY_EV_F9)
        elif (key == "F10"):
            self.emit_message(msgs.HWKEY_EV_F10)
        elif (key == "F11"):
            self.emit_message(msgs.HWKEY_EV_F11)
        elif (key == "F12"):
            self.emit_message(msgs.HWKEY_EV_F12)
            self.emit_message(msgs.HWKEY_EV_EJECT)  # deprecated
            
        elif (key == "Up"):
            self.emit_message(msgs.HWKEY_EV_UP)
        elif (key == "Down"):
            self.emit_message(msgs.HWKEY_EV_DOWN)
        elif (key == "Left"):
            self.emit_message(msgs.HWKEY_EV_LEFT)
        elif (key == "Right"):
             self.emit_message(msgs.HWKEY_EV_RIGHT)

            
        elif (key == "XF86Headset"):
            self.emit_message(msgs.HWKEY_EV_HEADSET)
            
        
        elif (key == "BackSpace"):
            self.emit_message(msgs.HWKEY_EV_BACKSPACE)
            term = self.__get_search_term()
            if (term):
                term = term[:-1]
                self.__set_search_term(term)
       
        elif (len(key) == 1 and ord(key) > 31):
            print "KEY", key
            self.emit_message(msgs.HWKEY_EV_KEY, key)
            term = self.__get_search_term()
            term += key.lower()
            self.__set_search_term(term)

        


    def __show_virtual_keyboard(self):
        """
        Displays the virtual keyboard.
        """
       
        self.emit_message(msgs.VKB_ACT_SHOW, self.__window)



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
            self.emit_message(msgs.CORE_ACT_SEARCH_ITEM, term)
            
    """
    def __on_observe_strip(self, src, cmd, *args):
    
        w, h = self.get_size()
        handled = False
        if (cmd == src.OBS_SCROLLING):
            # invalidate ticket
            self.__ticket = 0
    
        elif (cmd == src.OBS_CLICKED):
            px, py = args
            if (30 <= py < h - 60 and px > 108):
                idx = self.__strip.get_index_at(py)
                vstate = self.__get_vstate()
                vstate.selected_item = idx
                self.__select_item(idx)
                handled = True
            elif (0 <= px <= 80 and py >= h - 60):
                self.emit_message(msgs.INPUT_EV_MENU)
                handled = True

        return handled        
    """


    def handle_message(self, event, *args):

        return
               
        """
        elif (event == msgs.UI_ACT_SET_STRIP):
            viewer, items = args
            vstate = self.__get_vstate(viewer)
            vstate.items = items
            vstate.selected_item = -1
            vstate.item_offset = 0
            if (viewer == self.__current_viewer):
                self.__set_collection(items)
                
        elif (event == msgs.UI_ACT_CHANGE_STRIP):
            owner = args[0]
            self.__strip.change_image_set(owner)
               
        elif (event == msgs.UI_ACT_HILIGHT_STRIP_ITEM):
            viewer, idx = args
            vstate = self.__get_vstate(viewer)
            vstate.selected_item = idx
            if (viewer == self.__current_viewer):
                self.__select_item(idx, hilight_only = True)
               
        elif (event == msgs.UI_ACT_SELECT_STRIP_ITEM):
            viewer, idx = args
            vstate = self.__get_vstate(viewer)
            vstate.selected_item = idx
            if (viewer == self.__current_viewer):
                self.__select_item(idx)

        elif (event == msgs.UI_ACT_SHOW_STRIP_ITEM):
            viewer, idx = args
            if (viewer == self.__current_viewer):
                self.__strip.scroll_to_item(idx)
        """
               
        """
        elif (event == msgs.CORE_ACT_SCROLL_UP):
            w, h = self.__strip.get_size()
            idx = self.__strip.get_index_at(h)
            if (idx != -1):
                new_idx = min(len(self.__strip.get_images()), idx + 2)
                self.__strip.scroll_to_item(new_idx)

        elif (event == msgs.CORE_ACT_SCROLL_DOWN):
            idx = self.__strip.get_index_at(0)
            if (idx != -1):
                new_idx = max(0, idx - 2)
                self.__strip.scroll_to_item(new_idx)

            
        elif (event == msgs.CORE_ACT_RENDER_ITEMS):
            self.__strip.invalidate_buffer()
            self.__strip.render()
        """



    def __get_vstate(self, viewer = None):
    
        if (not viewer):
            viewer = self.__current_viewer
       
        if (not viewer in self.__viewer_states):
            vstate = ViewerState()
            self.__viewer_states[viewer] = vstate
        
        return self.__viewer_states[viewer]
                
            
            
    """
    def __select_item(self, idx, hilight_only = False):

        self.__hilight_item(idx)

        if (not hilight_only):
            self.emit_message(msgs.CORE_ACT_LOAD_ITEM, idx)
            
        self.__strip.scroll_to_item(idx)
    """


    """
    def __hilight_item(self, idx):
    
        self.__strip.hilight(idx)
    """
 
 
    def __select_viewer_by_name(self, name):
        """
        Selects the current viewer by name.
        """
        
        viewers = [ v for v in self.__viewers if repr(v) == name ]
        if (viewers):
            idx = self.__viewers.index(viewers[0])
            self.__select_viewer(idx)
        else:
            self.__select_viewer(0)
            

            
    def __select_viewer(self, idx):
        """
        Selects the current viewer by index number.
        """        
      
        viewer = self.__viewers[idx]
        
        if (self.__current_viewer):
            self.__current_viewer.hide()
            #self.__get_vstate().item_offset = self.__strip.get_offset()
                
        self.__current_viewer = viewer
        #self.__kscr.stop_scrolling()

        vstate = self.__get_vstate()
        self.__set_view_mode(vstate.view_mode)

        self.set_frozen(True)
        viewer.show()
        
        #self.__strip.set_offset(vstate.item_offset)
        #if (vstate.selected_item >= 0):
        #    self.__hilight_item(vstate.selected_item)
        
        self.set_frozen(False)
        self.fx_slide_in()
        #self.render_buffered()
        
        self.emit_message(msgs.INPUT_ACT_REPORT_CONTEXT)
        self.emit_message(msgs.UI_EV_VIEWER_CHANGED, idx)


    """
    def __set_collection(self, collection):
        ""
        Loads the given collection into the item strip.
        ""

        self.__hilight_item(-1)
        thumbnails = collection        
        self.__strip.set_images(thumbnails)
        self.__strip.render()

        # if the collection is empty, tell the user that she can add items
        #if (not collection and self.__view_mode == viewmodes.NORMAL):
        #    gobject.idle_add(dialogs.info, "No items found!",
        #              "There are no items.\n"
        #              "Please go to Media Collection in the Preferences view\n"
        #              "to tell MediaBox where to look for your files.")
    """
        
        
    def __try_quit(self):
    
        self.__window.present()
        result = self.call_service(msgs.DIALOG_SVC_QUESTION,
                                   "Exit",
                                   "Do you want to quit MediaBox?")

        if (result == 0):
            config.set_current_viewer(self.__current_viewer)
            config.set_current_device(self.__current_device_id)
            self.emit_message(msgs.MEDIA_ACT_STOP)
            self.emit_message(msgs.CORE_EV_APP_SHUTDOWN)
            gtk.main_quit()
        else:
            pass


    def handle_COM_EV_COMPONENT_LOADED(self, component):
    
        if (isinstance(component, Viewer)):
            self.__viewers.append(component)
        elif (isinstance(component, Widget)):
            self.add(component)


    def handle_CORE_ACT_APP_MINIMIZE(self):

        self.__window.iconify()
        
        
    def handle_CORE_ACT_APP_CLOSE(self):

        self.__try_quit()


    def handle_CORE_ACT_SCAN_MEDIA(self, force_rebuild):

        self.__scan_media(force_rebuild)



    def handle_CORE_EV_THEME_CHANGED(self):

        from mediabox import thumbnail
        thumbnail.clear_cache()
        #self.set_frozen(True)
        self.propagate_theme_change()
        #self.__prepare_collection_caps()
        #self.__root_pane.render_buffered()            
        self.fx_slide_in()


    def handle_CORE_ACT_SET_TITLE(self, title):

        self.__title_panel.set_title(title)


    def handle_CORE_ACT_SET_INFO(self, info):

        self.__title_panel.set_info(info)


    def handle_CORE_ACT_SET_TOOLBAR(self, tbset):

        self.__ctrl_panel.set_toolbar(tbset)


    def handle_HWKEY_EV_BACKSPACE(self):

        term = self.__get_search_term()
        if (term):
            term = term[:-1]
            self.__set_search_term(term)

    def handle_HWKEY_EV_KEY(self, key):

        term = self.__get_search_term()
        term += key.lower()
        self.__set_search_term(term)


    def handle_INPUT_EV_PREVIOUS_VIEWER(self):            

        idx = self.__viewers.index(self.__current_viewer)
        if (idx > 0):
            self.__select_viewer(idx - 1)
                
    def handle_INPUT_EV_NEXT_VIEWER(self):

        idx = self.__viewers.index(self.__current_viewer)
        if (idx < len(self.__viewers) - 1):
            self.__select_viewer(idx + 1)


    def handle_MEDIA_EV_VOLUME_CHANGED(self, percent):

        self.__title_panel.set_volume(percent)


    def handle_MEDIASCANNER_EV_SCANNING_STARTED(self):

        self.show_overlay("Scanning Media", "", theme.mb_viewer_audio)
        
        
    def handle_MEDIASCANNER_EV_SCANNING_PROGRESS(self, name):

        self.show_overlay("Scanning Media", "- %s -" % name,
                          theme.mb_viewer_audio)

    
    def handle_MEDIASCANNER_EV_SCANNING_FINISHED(self):

        self.hide_overlay()


    def handle_SYSTEM_EV_BATTERY_REMAINING(self, percent):                

        self.__battery_remaining = percent
        #self.__prepare_collection_caps()


    def handle_UI_EV_DEVICE_SELECTED(self, dev_id):    

        self.__current_device_id = dev_id


    def handle_UI_ACT_FREEZE(self):
    
        self.__box.set_frozen(True)

    
    def handle_UI_ACT_THAW(self):            

        self.__box.set_frozen(False)
        self.render_buffered()

    
    def handle_UI_ACT_RENDER(self):            

        self.render_buffered()


    def handle_UI_ACT_SHOW_MESSAGE(self, text, subtext, icon):

        self.show_overlay(text, subtext, icon)


    def handle_UI_ACT_HIDE_MESSAGE(self):

        self.hide_overlay()


    def handle_UI_ACT_SELECT_VIEWER(self, name):

        self.__select_viewer_by_name(name)


    def handle_UI_ACT_VIEW_MODE(self, mode):

        self.__set_view_mode(mode)


    def handle_UI_ACT_SET_STATUS_ICON(self, w):
    
        self.__title_panel.set_status_icon(w)
        

    def handle_UI_ACT_UNSET_STATUS_ICON(self, w):
    
        self.__title_panel.unset_status_icon(w)

