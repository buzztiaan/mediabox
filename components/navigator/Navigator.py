from com import View, msgs
from RootDevice import RootDevice
from mediabox.StorageBrowser import StorageBrowser
from ui.ImageButton import ImageButton
from ui.Slider import Slider
from ui.Toolbar import Toolbar
from ui.dialog import OptionDialog
from utils import mimetypes
from utils import logging
from mediabox import config as mb_config
from theme import theme

import random
import time


class Navigator(View):

    ICON = theme.mb_viewer_audio
    TITLE = "Navigator"
    PRIORITY = 0

    def __init__(self):
    
        # the file that is currently playing    
        self.__current_file = None

        # list for choosing random files from when in shuffle mode
        self.__random_files = []
        
        self.__is_searching = False
        self.__search_term = ""
        
        self.__key_hold_down_timestamp = 0
        self.__skip_letter = False

    
        View.__init__(self)

        # browser list slider
        self.__browser_slider = Slider(theme.mb_list_slider)
        self.__browser_slider.set_mode(Slider.VERTICAL)
        self.add(self.__browser_slider)

        
        # file browser
        self.__browser = StorageBrowser()
        self.__browser.associate_with_slider(self.__browser_slider)
        self.__browser.connect_folder_opened(self.__on_open_folder)
        self.__browser.connect_file_opened(self.__on_open_file)
        self.__browser.connect_file_enqueued(self.__on_enqueue_file)
        self.__browser.connect_thumbnail_requested(self.__on_request_thumbnail)
        self.__browser_slider.connect_button_pressed(
                                    lambda a,b:self.__browser.stop_scrolling())
        self.add(self.__browser)


        # toolbar
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)

        self.__btn_home = ImageButton(theme.mb_btn_home_1,
                                      theme.mb_btn_home_2)
        self.__btn_home.connect_clicked(self.__on_btn_home)
        
        self.__btn_history = ImageButton(theme.mb_btn_home_1,
                                         theme.mb_btn_home_2)
        self.__btn_history.connect_clicked(self.__on_btn_history)

        self.__btn_bookmarks = ImageButton(theme.mb_btn_bookmark_1,
                                           theme.mb_btn_bookmark_2)
        self.__btn_bookmarks.connect_clicked(self.__on_btn_bookmarks)

        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__btn_add = ImageButton(theme.mb_btn_add_1,
                                     theme.mb_btn_add_2)
        self.__btn_add.set_visible(False)
        self.__btn_add.connect_clicked(self.__on_btn_add)

       
        self.__browser.set_root_device(RootDevice())


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """

        cwd = self.__browser.get_current_folder()
        items = [self.__btn_home, self.__btn_history, self.__btn_back]
        
        if (cwd.folder_flags & cwd.ITEMS_ADDABLE):
            items.append(self.__btn_add)

        self.__toolbar.set_toolbar(*items)

            
    def show(self):
    
        View.show(self)
        names = [ p.name for p in self.__browser.get_path() ]
        #title = u" \u00bb ".join(names)
        title = names[-1]
        #self.set_title(title)

        self.__update_toolbar()
        self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)

       
    def __on_open_file(self, f):
    
        self.__load_file(f)


    def __on_open_folder(self, f):

        if (self.__browser.is_visible()):
            names = [ p.name for p in self.__browser.get_path() ]
            #title = u" \u00bb ".join(names)
            title = names[-1]
            names.reverse()
            acoustic_title = "Entering " + " in ".join(names)
            #self.set_title(title)
            self.emit_message(msgs.UI_ACT_TALK, acoustic_title)
            self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
            self.__update_toolbar()
        #end if
        
        self.__random_files = []


    def __on_enqueue_file(self, f):
    
        print "ENQ"
        dlg = OptionDialog("Select a Playlist")
        playlists = self.call_service(msgs.PLAYLIST_SVC_GET_LISTS)
        print playlists
        if (not playlists): return
        
        # select playlist
        if (len(playlists) == 1):
            playlist = playlists[0]
        
        else:
            for pl in playlists:
                dlg.add_option(None, pl)
            if (dlg.run() == 0):
                choice = dlg.get_choice()
                playlist = playlists[choice]
        #end for
    
        self.emit_message(msgs.PLAYLIST_ACT_APPEND, playlist, f)
        

    def __on_request_thumbnail(self, f, async_required, cb):

        if (async_required):
            # create thumbnail
            self.call_service(msgs.MEDIASCANNER_SVC_LOAD_THUMBNAIL, f, cb)
            return None
            
        else:
            # lookup existing thumbnail
            thumbnail = self.call_service(
                msgs.MEDIASCANNER_SVC_LOOKUP_THUMBNAIL, f) or None
            return thumbnail


    def __on_btn_home(self):
        """
        Reacts on pressing the [Home] button.
        """

        self.__browser.go_root()
        
        
    def __on_btn_history(self):
        """
        Reacts on pressing the [History] button.
        """
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, "history:///")
        if (f):
            self.__browser.load_folder(f, self.__browser.GO_PARENT, True)


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

            
            
    def __on_btn_add(self):
        """
        Reacts on pressing the [Add] button.
        """
        
        folder = self.__browser.get_current_folder()
        if (folder):
            f = folder.new_file()
        #    if (f):
        #        self.__browser.reload_current_folder()
        




    def __load_file(self, f):
        """
        Loads the given file.
        """

        self.__current_file = f
        self.__browser.hilight_file(f)

        if (not f.mimetype in mimetypes.get_image_types()):
            self.emit_message(msgs.MEDIA_ACT_STOP)

        self.emit_message(msgs.MEDIA_ACT_LOAD, f)
        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)


    def render_this(self):
    
        w, h = self.get_size()
        if (w < h):
            # portrait mode
            self.__browser_slider.set_geometry(0, 0, 40, h - 70)
            self.__browser.set_geometry(40, 0, w - 40, h - 70)
            self.__toolbar.set_geometry(0, h - 70, w, 70)

        else:
            # landscape mode
            self.__browser_slider.set_geometry(0, 0, 40, h)
            self.__browser.set_geometry(40, 0, w - 40 - 70, h)
            self.__toolbar.set_geometry(w - 70, 0, 70, h)


    def __go_previous(self):

        playable_files = [ f for f in self.__browser.get_files()
                           if not f.mimetype.endswith("-folder") ]

        try:
            idx = playable_files.index(self.__current_file)
        except ValueError:
            return False
            
        if (idx > 0):
            next_item = playable_files[idx - 1]
            self.__load_file(next_item)
            
            
    def __go_next(self):

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
            

    def __play_same(self):
    
        self.__load_file(self.__current_file)

        return True
        
        
    def __play_next(self, wraparound):
    
        playable_files = [ f for f in self.__browser.get_files()
                           if not f.mimetype.endswith("-folder") ]
        try:
            idx = playable_files.index(self.__current_file)
        except:
            idx = -1
        

        if (idx + 1 < len(playable_files)):
            next_item = playable_files[idx + 1]
            self.__load_file(next_item)
            return True

        elif (wraparound):
            next_item = playable_files[0]
            self.__load_file(next_item)
            return True
            
        else:
            return False

        
        
    def __play_shuffled(self, from_all):
    
        if (from_all):
            # TODO...
            pass

        if (not self.__random_files):
            self.__random_files = [ f for f in self.__browser.get_files()
                                    if not f.mimetype.endswith("-folder") ]

        idx = random.randint(0, len(self.__random_files) - 1)
        next_item = self.__random_files.pop(idx)
        self.__load_file(next_item)
        
        return True

      

    def handle_CORE_EV_FOLDER_INVALIDATED(self, folder):
    
        self.__browser.invalidate_folder(folder)


    def handle_CORE_EV_DEVICE_REMOVED(self, dev_id):
    
        folder = self.__browser.get_current_folder()
        if (folder.device_id == dev_id):
            self.__browser.go_root()
        


    def handle_CORE_ACT_SEARCH_ITEM(self, key):
    
        if (self.is_active()):
            #self.__browser.set_message("Search: " + key)
            if (key != self.__search_term):
                self.__browser.set_cursor(1)
            idx = self.__browser.search(key, 1)
            if (idx != -1):
                self.__browser.set_cursor(idx)
                self.__browser.scroll_to_item(idx)
            self.__is_searching = True
            self.__search_term = key
        #end if


    def handle_CORE_EV_SEARCH_CLOSED(self):
    
        #self.__browser.set_message("")
        self.__browser.search("", 1)
        self.__browser.render()
        self.__is_searching = False
        self.__search_term = ""

    
    def handle_MEDIA_EV_LOADED(self, viewer, f):
    
        pass


    def handle_MEDIA_ACT_PREVIOUS(self):
    
        self.__go_previous()
  
  
    def handle_MEDIA_ACT_NEXT(self):
    
        self.__go_next()
  
          

    def handle_INPUT_ACT_REPORT_CONTEXT(self):
    
        if (self.is_active()):
            self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)



    def handle_INPUT_EV_UP(self):

        if (not self.is_active()): return

        now = time.time()
        #if (now < self.__key_hold_down_timestamp + 0.1):
        #    self.__skip_letter = True
        #elif (now > self.__key_hold_down_timestamp + 0.5):
        self.__skip_letter = False
        self.__key_hold_down_timestamp = now

        if (self.__is_searching):
            idx = self.__browser.search(self.__search_term, -1)
            if (idx != -1):
                self.__browser.set_cursor(idx)
                #self.__browser.scroll_to_item(idx)
            
        else:
            self.__browser.move_cursor(-1, self.__skip_letter)
            cursor = self.__browser.get_cursor()
            item = self.__browser.get_item(cursor)
            f = item.get_file()
            self.emit_message(msgs.UI_ACT_TALK, f.acoustic_name or f.name)
            

    def handle_INPUT_EV_PAGE_UP(self):

        if (self.is_active()):        
            idx = self.__browser.get_index_at(0)
            if (idx != -1):
                new_idx = max(0, idx - 2)
                self.__browser.scroll_to_item(new_idx)


    def handle_INPUT_EV_DOWN(self):

        if (not self.is_active()): return

        now = time.time()
        #if (now < self.__key_hold_down_timestamp + 0.1):
        #    self.__skip_letter = True
        #elif (now > self.__key_hold_down_timestamp + 0.5):
        self.__skip_letter = False
        self.__key_hold_down_timestamp = now
        
        if (self.__is_searching):
            idx = self.__browser.search(self.__search_term, 1)
            if (idx != -1):            
                self.__browser.set_cursor(idx)
                #self.__browser.scroll_to_item(idx)
            
        else:
            self.__browser.move_cursor(1, self.__skip_letter)
            cursor = self.__browser.get_cursor()
            item = self.__browser.get_item(cursor)
            f = item.get_file()
            self.emit_message(msgs.UI_ACT_TALK, f.acoustic_name or f.name)



    def handle_INPUT_EV_PAGE_DOWN(self):
    
        if (self.is_active()):
            w, h = self.__browser.get_size()
            idx = self.__browser.get_index_at(h)
            if (idx != -1):
                items = self.__browser.get_items()
                new_idx = min(len(items), idx + 2)
                self.__browser.scroll_to_item(new_idx)


    def handle_INPUT_EV_RIGHT(self):
    
        if (self.is_active()):
            self.select_tab(1)


    def handle_INPUT_EV_ENTER(self):
    
        if (self.is_active()):
            cursor = self.__browser.get_cursor()
            if (cursor != -1):
                self.__browser.trigger_item_button(cursor)

    
    def handle_INPUT_EV_GO_PARENT(self):
    
        if (self.is_active()):
            self.__browser.go_parent()

