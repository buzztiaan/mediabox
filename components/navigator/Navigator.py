from com import Component, Dialog, Widget, msgs
from NowPlaying import NowPlaying
from RootDevice import RootDevice
from mediabox.StorageBrowser import StorageBrowser
from ui.Button import Button
from ui.ImageButton import ImageButton
from ui.Toolbar import Toolbar
from ui.dialog import InputDialog
from ui.dialog import InfoDialog
from ui.layout import Arrangement
from ui import Window
from ui import windowflags
from utils import mimetypes
from utils import logging
from storage import File
from mediabox import config as mb_config
from mediabox import values
from utils.ItemScheduler import ItemScheduler
from utils import mimetypes
from utils import state
import platforms
from theme import theme

import gobject
import gtk
import random
import time
import os


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar"
            x1="-80" y1="0" x2="100%" y2="100%"/>

    <widget name="now-playing"
            x1="-160" y1="0" x2="-80" y2="100%"/>

    <widget name="browser"
            x1="0" y1="0" x2="-160" y2="100%"/>
  </arrangement>
"""


_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar"
            x1="0" y1="-80" x2="100%" y2="100%"/>

    <widget name="now-playing"
            x1="0" y1="0" x2="100%" y2="80"/>

    <widget name="browser"
            x1="0" y1="80" x2="100%" y2="-80"/>
  </arrangement>
"""

_STATEFILE = os.path.join(values.USER_DIR, "navigator-state")

_MODE_NORMAL = 0
_MODE_SELECT = 1


# it's useful to swap the mapping of the increment and decrement keys in
# portrait mode
_PORTRAIT_MODE_KEYSWAP = {
    "F7": "F8",
    "F8": "F7"
}


class Navigator(Component, Window):
    """
    Navigator dialog for browsing media.
    """

    def __init__(self):
    
        # the current mode
        self.__mode = _MODE_NORMAL
        
        # list of available dialog windows
        self.__dialogs = []
        
        self.__widgets = []
        
        # the file that is currently playing    
        self.__current_file = None

        # list of files for playing
        self.__play_folder = None
        self.__play_files = []

        # list for choosing random files from when in shuffle mode
        self.__random_files = []

        # current window size (for detecting resizing)
        self.__window_size = (0, 0)
        
        self.__is_searching = False
        self.__filter_term = ""
        
        self.__key_hold_down_timestamp = 0
        self.__skip_letter = False
        
        # scheduler for creating thumbnails one by one
        self.__tn_scheduler = ItemScheduler()
        
        # whether we are shutting down
        self.__is_shutdown = False
        
    
        Component.__init__(self)
        Window.__init__(self, Window.TYPE_TOPLEVEL)
        self.set_flag(windowflags.CATCH_VOLUME_KEYS, True)
        self.connect_key_pressed(self.__on_key_press)
        self.connect_closed(self.__on_close_window)

        # [Now Playing] button
        self.__now_playing = NowPlaying()
        #self.__now_playing.set_visible(False)

        
        # file browser
        self.__browser = StorageBrowser()
        #self.__browser.set_root_device(self.__root_dev)
        self.__browser.connect_folder_begin(self.__on_begin_folder)
        self.__browser.connect_folder_progress(self.__on_progress_folder)
        self.__browser.connect_folder_complete(self.__on_complete_folder)
        self.__browser.connect_file_opened(self.__on_open_file)
        self.__browser.connect_item_shifted(self.__on_shift_item)

        # toolbar
        self.__toolbar = Toolbar()

        self.__btn_home = ImageButton(theme.mb_btn_home_1,
                                      theme.mb_btn_home_2)
        self.__btn_home.connect_clicked(self.__on_btn_home)
        
        self.__btn_history = ImageButton(theme.mb_btn_history_1,
                                         theme.mb_btn_history_2)
        self.__btn_history.connect_clicked(self.__on_btn_history)

        self.__btn_bookmarks = ImageButton(theme.mb_btn_bookmark_1,
                                           theme.mb_btn_bookmark_2)
        self.__btn_bookmarks.connect_clicked(self.__on_btn_bookmarks)

        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__btn_select_all = ImageButton(theme.mb_btn_select_all_1,
                                            theme.mb_btn_select_all_2)
        self.__btn_select_all.connect_clicked(self.__on_btn_select_all)

        self.__btn_select_none = ImageButton(theme.mb_btn_select_none_1,
                                             theme.mb_btn_select_none_2)
        self.__btn_select_none.connect_clicked(self.__on_btn_select_none)

        self.__btn_select_done = ImageButton(theme.mb_btn_select_done_1,
                                             theme.mb_btn_select_done_2)
        self.__btn_select_done.connect_clicked(self.__on_btn_select_done)


        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__now_playing, "now-playing")
        self.__arr.add(self.__browser, "browser")
        self.__arr.add(self.__toolbar, "toolbar")
        self.add(self.__arr)
        self.__arr.set_visible(False)

        # we have to fill the menu with content before showing the window on
        # Maemo5 or the window will show no menu at all
        self.__update_menu()
        
        self.set_visible(True)


    def __update_menu(self):

        folder = self.__browser.get_current_folder()
        
        repeat_selected = [mb_config.REPEAT_MODE_NONE,
                           mb_config.REPEAT_MODE_ALL,
                           mb_config.REPEAT_MODE_ONE] \
                          .index(mb_config.repeat_mode())
        shuffle_selected = [mb_config.SHUFFLE_MODE_NONE,
                            mb_config.SHUFFLE_MODE_ONE] \
                           .index(mb_config.shuffle_mode())
                           
        self.set_menu_choice("repeat", [(theme.mb_repeat_none, "No Repeat"),
                                        (theme.mb_repeat_all, "Repeat All"),
                                        (theme.mb_repeat_one, "Repeat One")],
                             repeat_selected, True,
                             self.__on_menu_repeat)
        self.set_menu_choice("shuffle", [(theme.mb_shuffle_none, "No Shuffle"),
                                        (theme.mb_shuffle_one, "Shuffle")],
                             shuffle_selected, True,
                             self.__on_menu_shuffle)
        
        if (folder and folder.folder_flags & folder.ITEMS_ADDABLE):          
            self.set_menu_item("add", "Add New", True,
                               self.__on_menu_add)
        else:
            self.set_menu_item("add", "Add New", False,
                               self.__on_menu_add)
        
        self.set_menu_item("openurl", "Open URL...", True,
                           self.__on_menu_open_url)
        
        self.set_menu_item("downloads", "Active Downloads", True,
                           self.__on_menu_downloads)

        self.set_menu_item("select", "Select Items for Action", True,
                           self.__on_menu_select)
        
        #self.set_menu_item("rearrange", "Rearrange Items", True,
        #                   self.__on_menu_rearrange)
        #self.set_menu_item("info", "About", True,
        #                   self.__on_menu_info)


    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            # portrait mode
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)
        else:
            # landscape mode
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """

        cwd = self.__browser.get_current_folder()
        if (self.__mode == _MODE_NORMAL):
            items = [self.__btn_home,
                     self.__btn_history,
                     self.__btn_back]
        else:
            items = [self.__btn_select_all,
                     self.__btn_select_none,
                     self.__btn_select_done]
        
        self.__toolbar.set_toolbar(*items)


    def __update_items_per_row(self, folder):

        w, h = self.get_size()
        
        if (folder and folder.folder_flags & folder.ITEMS_COMPACT):
            if (w > 0):
                per_row = w / 160
            else:
                per_row = 3
            #if (w < h):
            self.__browser.set_items_per_row(per_row)
            #else:
            #    self.__browser.set_items_per_row(4)
        else:
            self.__browser.set_items_per_row(1)
            
        #self.__browser.invalidate()
        #self.__browser.render()


    """
    def _visibility_changed(self):
        
        Window._visibility_changed(self)
        if (self.is_visible()):
            self.__tn_scheduler.resume()
            
        else:
            self.__tn_scheduler.halt()
    """


    def __on_key_press(self, keycode):

        w, h = self.get_size()
        if (w < h and
              mb_config.portrait_swap_volume() and
              keycode in _PORTRAIT_MODE_KEYSWAP):
            keycode = _PORTRAIT_MODE_KEYSWAP[keycode]

        handled = self.call_service(msgs.INPUT_SVC_SEND_KEY, keycode, True)
        if (not handled):
            """
            if (len(keycode) == 1 and ord(keycode) > 31):
                cnt = 0
                for item in self.__browser.get_items():
                    if (item.get_name().upper().startswith(keycode.upper())):
                        self.__browser.scroll_to_item(cnt)
                        break
                    cnt += 1
                #end for
            """    
            if (len(keycode) == 1 and ord(keycode) > 31):
                self.__filter_term += keycode
                self.__update_filter()
            elif (keycode == "BackSpace" and self.__filter_term):
                self.__filter_term = self.__filter_term[:len(self.__filter_term) - 1]
                self.__update_filter()


    def __update_filter(self):

        def filter_func(item):
            return self.__filter_term.upper() in item.get_name().upper() + "#" + \
                                                 item.get_file().info.upper()

        if (self.__filter_term):
            self.__browser.set_filter(filter_func)
            self.__browser.set_message("Filter: %s (%d matches)" \
                                       % (self.__filter_term,
                                          self.__browser.count_items()))
        else:
            self.__browser.set_filter()
            self.__browser.set_message("")
                
        self.__browser.invalidate()
        self.__browser.render()




    def __on_close_window(self):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.emit_message(msgs.COM_EV_APP_SHUTDOWN)
        gtk.main_quit()


    def __on_menu_repeat(self, choice):
    
        if (choice == 0):
            mb_config.set_repeat_mode(mb_config.REPEAT_MODE_NONE)
        elif (choice == 1):
            mb_config.set_repeat_mode(mb_config.REPEAT_MODE_ALL)
        elif (choice == 2):
            mb_config.set_repeat_mode(mb_config.REPEAT_MODE_ONE)
        
        
    def __on_menu_shuffle(self, choice):
    
        if (choice == 0):
            mb_config.set_shuffle_mode(mb_config.SHUFFLE_MODE_NONE)
        elif (choice == 1):
            mb_config.set_shuffle_mode(mb_config.SHUFFLE_MODE_ONE)


    def __on_menu_rearrange(self):
    
        def on_done():
            for item in self.__browser.get_items():
                item.set_draggable(False)
            self.__browser.invalidate()
                
            self.__update_toolbar()
    
        for item in self.__browser.get_items():
            item.set_draggable(True)
        self.__browser.invalidate()
    
        btn_done = ImageButton(theme.mb_btn_history_1,
                               theme.mb_btn_history_2)
        btn_done.connect_clicked(on_done)
        self.__toolbar.set_toolbar(btn_done)


    def __on_menu_open_url(self):
    
        dlg = InputDialog("URL to open")
        dlg.add_input("URL", "http://")
        
        if (dlg.run() == dlg.RETURN_OK):
            url = dlg.get_values()[0]
            self.__load_uri(url, "")
        #end if
        

    def __on_menu_downloads(self):
    
        self.emit_message(msgs.UI_ACT_SHOW_DIALOG, "downloader.DownloadManager")
        
        
    def __on_menu_fmtx(self):
    
        import platforms
        platforms.plugin_execute("libcpfmtx.so")


    def __on_menu_select(self):
        
        if (self.__browser.begin_bulk_action()):
            self.__mode = _MODE_SELECT
            self.__update_toolbar()
        #end if


    def __on_menu_add(self):
        
        folder = self.__browser.get_current_folder()
        if (folder):
            folder.new_file()
 
 
    def __on_menu_info(self):
    
        self.__show_dialog("core.AboutDialog")
 
       
    def __on_open_file(self, f):
            
        self.__load_file(f, True)


    def __on_begin_folder(self, f):
        
        self.__tn_scheduler.new_schedule(70, self.__on_load_thumbnail)
        self.__tn_scheduler.halt()
        
        self.set_flag(windowflags.BUSY, True)
        
        self.__browser.set_filter()
        self.__filter_term = ""
        
        self.__update_layout()
        self.__update_menu()
        
        self.__update_items_per_row(f)
        self.__browser.render()

        # set platform-specific click behavior
        if (platforms.MAEMO4):
            self.__browser.set_click_behavior(
              self.__browser.CLICK_BEHAVIOR_DOUBLE)
        else:
            self.__browser.set_click_behavior(
              self.__browser.CLICK_BEHAVIOR_SINGLE)
                

    def __on_progress_folder(self, f, c):
    
        if (not c.icon):
            items = self.__browser.get_items()
            item = items[-1]
            
            # process the first few items at once to give a better impression
            # of speed
            if (len(items) <= 16):
                thumbpath, is_final = \
                  self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, c)

                item.set_icon(thumbpath)
            
                if (not is_final):
                    self.__tn_scheduler.add(item, c, False)

            else:
                self.__tn_scheduler.add(item, c, True)
        #end if


    def __on_complete_folder(self, f):

        self.set_flag(windowflags.BUSY, False)
        
        names = [ p.name for p in self.__browser.get_path() ]
        #title = u" \u00bb ".join(names)
        title = names[-1]
        names.reverse()
        acoustic_title = "Entering " + " in ".join(names)
        self.set_title(title)
        self.emit_message(msgs.UI_ACT_TALK, acoustic_title)
        self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
        self.__update_toolbar()

        if (self.is_visible()):
            self.__tn_scheduler.resume()


    def __on_shift_item(self, pos, amount):
    
        if (self.get_current_folder() == self.__play_folder):
            # force invalidation of play files
            self.__play_files = []


    def __update_thumbnail(self, item, thumbpath):
    
        item.set_icon(thumbpath)
        try:
            idx = self.__browser.get_items().index(item)
            self.__browser.invalidate_item(idx)
        except:
            pass


    def __on_load_thumbnail(self, item, f, quick):

        def on_loaded(thumbpath):
            if (thumbpath):
                self.__update_thumbnail(item, thumbpath)
            
            # priorize visible items
            top_idx = self.__browser.get_item_at(0, 0)
            if (top_idx != -1):
                items = self.__browser.get_items()
                if (top_idx < len(items)):
                    self.__tn_scheduler.priorize(items[top_idx:top_idx + 12])
            #end if
            
            self.__tn_scheduler.resume()
    
        # load thumbnail
        self.__tn_scheduler.halt()
        if (quick):
            thumbpath, is_final = \
              self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
            item.set_icon(thumbpath)
            item.render_at(None, 0, 0)
            idx = self.__browser.get_items().index(item)
            self.__browser.invalidate_item(idx)
            
            # priorize visible items
            top_idx = self.__browser.get_item_at(0, 0)
            if (top_idx != -1):
                items = self.__browser.get_items()
                if (top_idx < len(items)):
                    self.__tn_scheduler.priorize(items[top_idx:top_idx + 12])
            #end if
            
            if (not is_final):
                #print "SCHEDULING THUMBNAIL", c
                self.__tn_scheduler.add(item, f, False)
            self.__tn_scheduler.resume()

        else:
            self.call_service(msgs.THUMBNAIL_SVC_LOAD_THUMBNAIL, f, on_loaded)
        

    def __on_btn_home(self):
        """
        Reacts on pressing the [Home] button.
        """

        self.emit_message(msgs.SSDP_ACT_SEARCH_DEVICES)
        self.__browser.go_root()
        
        
    def __on_btn_history(self):
        """
        Reacts on pressing the [History] button.
        """
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, "history:///")
        if (f):
            self.__browser.load_folder(f, self.__browser.GO_CHILD, True)


    def __on_btn_bookmarks(self):
        """
        Reacts on pressing the [Bookmarks] button.
        """
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, "bookmarks://generic/")
        if (f):
            self.__browser.load_folder(f, self.__browser.GO_PARENT, True)


    def __on_btn_back(self):
        """
        Reacts on pressing the [Back] button.
        """

        self.__browser.go_parent()
        #self.__update_items_per_row(self.__browser.get_current_folder())


    def __on_btn_select_all(self):  
        """
        Reacts on pressing the [Select All] button.
        """
        
        self.__browser.select_all()
        
        
    def __on_btn_select_none(self):
        """
        Reacts on pressing the [Select None] button.
        """
        
        self.__browser.unselect_all()
        
        
    def __on_btn_select_done(self):
        """
        Reacts on pressing the [Select Done] button.
        """

        self.__mode = _MODE_NORMAL
        self.__update_toolbar()
        self.__browser.perform_bulk_action()


    def __load_uri(self, uri, mimetype):
    
        if (not mimetype):
            ext = os.path.splitext(uri)[1]
            mimetype = mimetypes.ext_to_mimetype(ext)
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE,
                              "adhoc://" + File.pack_path("/", uri, mimetype))
        print "Loading URI:", f
        if (f):
            self.__load_file(f, True)



    def __load_file(self, f, is_manual):
        """
        Loads the given file.
        """

        #if (f.mimetype == "application/x-applet"):
        #    applet_id = f.resource
        #    self.call_service(msgs.CORE_SVC_LAUNCH_APPLET, applet_id)

        stopwatch = logging.stopwatch()
        
        if (f.mimetype == f.CONFIGURATOR):
            cfg_name = f.resource
            self.emit_message(msgs.UI_ACT_SHOW_DIALOG, cfg_name)

        else:
            if (is_manual):
                self.__show_dialog("player.PlayerWindow")
                
            #if (not f.mimetype in mimetypes.get_image_types()):
            self.emit_message(msgs.MEDIA_ACT_STOP)
            self.emit_message(msgs.MEDIA_ACT_LOAD, f)

            # update set of play files
            self.__current_file = f

            folder = self.__browser.get_current_folder()
            if (is_manual and folder != self.__play_folder):
                self.__play_folder = folder
                self.__random_files = []
                self.__invalidate_play_files()
        
        logging.profile(stopwatch, "[navigator] loaded file")


    def __go_previous(self):

        now = time.time()
        if (not self.__play_files):
            self.__invalidate_play_files()
        
        try:
            idx = self.__play_files.index(self.__current_file)
        except ValueError:
            return False
            
        if (idx > 0):
            next_item = self.__play_files[idx - 1]
            self.__load_file(next_item, False)
            
        logging.profile(now, "[navigator] loaded previous item")
            
            
    def __go_next(self):

        stopwatch = logging.stopwatch()
        if (not self.__play_files):
            self.__invalidate_play_files()
        
        repeat_mode = mb_config.repeat_mode()
        shuffle_mode = mb_config.shuffle_mode()
        
        if (repeat_mode == mb_config.REPEAT_MODE_NONE):
            if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                self.__play_next(False)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                self.__play_shuffled(False)
                
            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                self.__play_shuffled(True)
            
        elif (repeat_mode == mb_config.REPEAT_MODE_ONE):
            if (self.__current_file):
                self.__play_same()
            else:
                self.__play_next(True)

        elif (repeat_mode == mb_config.REPEAT_MODE_ALL):
            if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                self.__play_next(True)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                self.__play_shuffled(False)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                self.__play_shuffled(True)
            
        logging.profile(stopwatch, "[navigator] loaded next item")
        

    def __play_same(self):
    
        self.__load_file(self.__current_file, False)

        return True
        
        
    def __play_next(self, wraparound):
    
        try:
            idx = self.__play_files.index(self.__current_file)
        except:
            idx = -1
        

        if (idx + 1 < len(self.__play_files)):
            next_item = self.__play_files[idx + 1]
            self.__load_file(next_item, False)
            return True

        elif (wraparound):
            next_item = self.__play_files[0]
            self.__load_file(next_item, False)
            return True
            
        else:
            self.__play_folder = self.get_current_folder()
            self.__invalidate_play_files()
            if (self.__play_files):
                next_item = self.__play_files[0]
                self.__load_file(next_item, False)
                return True
            else:
                return False

        
        
    def __play_shuffled(self, from_all):
    
        if (from_all):
            # TODO...
            pass

        if (not self.__random_files):
            self.__random_files = self.__play_files[:]

        idx = random.randint(0, len(self.__random_files) - 1)
        next_item = self.__random_files.pop(idx)
        logging.debug("[navigator] picking random item %d of %d: %s",
                      idx, len(self.__random_files), str(next_item))

        self.__load_file(next_item, False)
        
        return True


    def __invalidate_play_files(self):
        """
        Invalidates the play files and random files and rebuilds them.
        """

        profile_now = time.time()
        
        prev_play_files = self.__play_files
        self.__play_files = [ f for f in self.__play_folder.get_children()
                              if not f.mimetype.endswith("-folder") ]

        size = len(self.__play_files)
        img_size = len([f for f in self.__play_files
                        if f.mimetype in mimetypes.get_image_types() ])
        ratio = img_size / float(size)
        
        if (ratio < 0.5):
            self.__play_files = [ f for f in self.__play_files
                             if not f.mimetype in mimetypes.get_image_types() ]

        new_files = [ f for f in self.__play_files if not f in prev_play_files ]

        self.__random_files = [ f for f in self.__random_files
                                if f in self.__play_files ] + new_files
        
        logging.profile(profile_now, "[navigator] invalidated list of files " \
                                     "to play")


    def __filter_play_files(self):
        """
        Filters the list of playfiles to see if there's cover art to remove
        from the list.
        """
        
        if (not self.__play_files): return
        
        now = time.time()
        
        size = len(self.__play_files)
        img_size = len([f for f in self.__play_files
                        if f.mimetype in mimetypes.get_image_types() ])
        ratio = img_size / float(size)
        
        if (ratio < 0.5):
            self.__play_files = [ f for f in self.__play_files
                             if not f.mimetype in mimetypes.get_image_types() ]

            self.__random_files = [ f for f in self.__random_files
                                    if f in self.__play_files ]

        logging.profile(now, "[navigator] filtered items to play " \
                             "(removed cover art)")


    def __show_dialog(self, name):
        """
        Shows the dialog with the given name.
        """

        #print name, self.__dialogs
        dialogs = [ d for d in self.__dialogs if repr(d) == name ]
        if (dialogs):
            dlg = dialogs[0]
            dlg.set_visible(True)
        #end if


    def __save_state(self):

        # save state for next start
        path = [ f.full_path for f in self.__browser.get_path_stack() ]
        play_files = [ f.full_path for f in self.__play_files ]
        
        state.save(_STATEFILE, path,
                               play_files,
                               self.__play_folder and self.__play_folder.full_path or "",
                               self.__current_file and self.__current_file.full_path or "")


    def render_this(self):
    
        w, h = self.get_size()
        
        if ((w, h) != self.__window_size):
            self.__update_items_per_row(self.__browser.get_current_folder())
            self.__window_size = (w, h)
    
        if (self.__arr.is_visible()):
            Window.render_this(self)
            
        elif (self.__is_shutdown):
            x, y = self.get_screen_pos()
            screen = self.get_screen()
        
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            screen.draw_centered_text(values.NAME + " " + values.VERSION,
                                      theme.font_mb_headline,
                                      x, h / 2 - 30, w, 30, theme.color_mb_text)
            screen.draw_centered_text(values.COPYRIGHT,
                                      theme.font_mb_plain,
                                      x, h / 2, w, 30, theme.color_mb_text)
            screen.draw_centered_text("Exiting...",
                                      theme.font_mb_plain,
                                      x, h - 80, w, 20, theme.color_mb_text)
            screen.fit_pixbuf(theme.mb_logo,
                              w - 120, h - 120, 120, 120)

        else:
            x, y = self.get_screen_pos()
            screen = self.get_screen()
        
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            screen.draw_centered_text(values.NAME + " " + values.VERSION,
                                      theme.font_mb_headline,
                                      x, h / 2 - 30, w, 30, theme.color_mb_text)
            screen.draw_centered_text(values.COPYRIGHT,
                                      theme.font_mb_plain,
                                      x, h / 2, w, 30, theme.color_mb_text)
            screen.draw_centered_text("Loading... Please Wait",
                                      theme.font_mb_plain,
                                      x, h - 80, w, 20, theme.color_mb_text)
            screen.fit_pixbuf(theme.mb_logo,
                              w - 120, h - 120, 120, 120)


    def handle_COM_EV_COMPONENT_LOADED(self, component):

        if (isinstance(component, Dialog)):
            if (repr(component) in [ repr(d) for d in self.__dialogs ]):
                logging.error("a dialog with ID '%s' exists already.",
                              repr(component))
            else:
                self.__dialogs.append(component)
                #component.set_parent_window(self)

        elif (isinstance(component, Widget)):
            if (repr(component) in [ repr(d) for d in self.__widgets ]):
                pass
            else:
                self.__widgets.append(component)


    def handle_COM_EV_APP_STARTED(self):
    
        logging.profile(values.START_TIME, "[app] startup complete")
    
        # load state
        try:
            path, play_files, play_folder, current_file = state.load(_STATEFILE)
            
            path_stack = []
            for p in path:
                f = self.call_service(msgs.CORE_SVC_GET_FILE, p)
                if (f):
                    path_stack.append(f)
                    self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
                #end if
            #end for
            self.__browser.set_path_stack(path_stack)
            
            #self.__play_files = [ self.call_service(msgs.CORE_SVC_GET_FILE, p)
            #                      for p in play_files
            #                      if self.call_service(msgs.CORE_SVC_GET_FILE, p) ]
            self.__play_folder = self.call_service(msgs.CORE_SVC_GET_FILE,
                                                   play_folder)
            self.__current_file = self.call_service(msgs.CORE_SVC_GET_FILE,
                                                    current_file)
            
        except:
            logging.warning("could not restore navigator state:\n%s",
                            logging.stacktrace())
        
    
        self.__arr.set_visible(True)
        self.render()
        
        if (values.uri and (values.uri.startswith("http://") or
                            os.path.exists(values.uri))):
            ext = os.path.splitext(values.uri)[1]
            mimetype = mimetypes.ext_to_mimetype(ext)
            f = self.call_service(msgs.CORE_SVC_GET_FILE,
                                  "adhoc://" + File.pack_path("/", values.uri,
                                                              mimetype))
            self.__load_file(f, True)
        #end if

    
    def handle_COM_EV_APP_SHUTDOWN(self):

        self.__is_shutdown = True
        #self.render()
        
        #while (gtk.events_pending()): gtk.main_iteration(True)
        self.__save_state()



    def handle_CORE_EV_DEVICE_ADDED(self, ident, device):
            
        if (repr(device) == "navigator.RootDevice"):
            self.__browser.set_root_device(device)
         

    def handle_UI_ACT_SHOW_INFO(self, msg):
    
        dlg = InfoDialog(msg, self)
        dlg.run()


    def handle_UI_ACT_SHOW_DIALOG(self, name):
    
        self.__show_dialog(name)
      

    def handle_CORE_EV_FOLDER_INVALIDATED(self, folder):

        logging.debug("[navigator] invalidating folder %s", str(folder))
        
        if (self.is_visible()):
            self.__browser.invalidate_folder(folder)
            
        if (folder and folder == self.__play_folder):
            self.__invalidate_play_files()
        
            """
            prev_play_files = self.__play_files[:]
            self.__play_files = [ fl for fl in folder.get_children()
                                  if not fl.mimetype.endswith("-folder") ]
            # remove from random files what's no longer there and add to random
            # files what's new in play files
            logging.debug("[navigator] updating random items after folder " \
                          "invalidation")
            l = len(self.__random_files)
            self.__random_files = [ f for f in self.__play_files
                                    if f in self.__random_files or
                                       f not in prev_play_files ]
            logging.debug("[navigator] previously %d random items, now %d",
                          l, len(self.__random_files))
            """


    def handle_CORE_EV_DEVICE_REMOVED(self, dev_id):
    
        folder = self.__browser.get_current_folder()
        if (folder.device_id == dev_id):
            self.__browser.go_root()


    def handle_ASR_ACT_ENABLE(self, value):
    
        self.set_flag(windowflags.ASR, value)


    def handle_ASR_EV_PORTRAIT(self):
        
        self.set_flag(windowflags.PORTRAIT, True)
        #self.__update_items_per_row(self.__browser.get_current_folder())


    def handle_ASR_EV_LANDSCAPE(self):

        self.set_flag(windowflags.PORTRAIT, False)
        #self.__update_items_per_row(self.__browser.get_current_folder())


    def handle_MEDIA_EV_LOADED(self, player, f):
        
        if (not self.__now_playing.is_visible()):
            self.__update_layout()
    
        self.__browser.hilight_file(f)
        self.__browser.render()

                    

    def handle_MEDIA_ACT_LOAD_URI(self, uri, mimetype):
    
        self.__load_uri(uri, mimetype)


    def handle_MEDIA_ACT_CHANGE_PLAY_FOLDER(self, folder):
    
        self.__play_folder = folder
        self.__play_files = [ fl for fl in self.__browser.get_files()
                              if not fl.mimetype.endswith("-folder") ]
        logging.debug("[navigator] clearing random items")
        self.__random_files = []
   
    
    def handle_MEDIA_ACT_PREVIOUS(self):
    
        self.__go_previous()
  
  
    def handle_MEDIA_ACT_NEXT(self):
    
        self.__go_next()


    def handle_INPUT_EV_UP(self, pressed):

        if (self.is_visible()):
            self.__browser.move(0, -80)


    def handle_INPUT_EV_DOWN(self, pressed):

        if (self.is_visible()):
            self.__browser.move(0, 80)


    def handle_INPUT_EV_KEY(self, key, pressed):
    
        if (self.is_visible()):
            print "GOT KEY", key

