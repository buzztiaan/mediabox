from MediaItem import MediaItem
from ui.itemview.ThumbableGridView import ThumbableGridView
from ui.Pixmap import Pixmap
from ui.dialog import OptionDialog
from ui.Pixmap import text_extents
from theme import theme
from utils.ItemScheduler import ItemScheduler
from utils import logging

import time
import gobject
import gtk


_STATUS_OK = 0
_STATUS_INCOMPLETE = 1
_STATUS_INVALID = 2


class StorageBrowser(ThumbableGridView):

    GO_NEW = 0
    GO_CHILD = 1
    GO_PARENT = 2
    
    EVENT_FOLDER_BEGIN = "folder-begin"
    EVENT_FOLDER_PROGRESS = "folder-progress"
    EVENT_FOLDER_COMPLETE = "folder-complete"

    EVENT_FILE_OPENED = "file-opened"
    EVENT_FILE_ENQUEUED = "file-enqueued"
    EVENT_FILE_REMOVED = "file-removed"
    EVENT_FILE_BOOKMARKED = "file-bookmarked"
    EVENT_FILE_ADDED_TO_LIBRARY = "file-added-to-library"
    

    def __init__(self):

        # list of tuples: (path, status)
        self.__path_stack = []

        # queue of items for prerendering
        self.__items_to_prerender = []
        self.__prerender_handler = None

        # the currently hilighted file
        self.__hilighted_file = None

        # handler for the bulk action
        self.__bulk_action_handler = None
        
        # whether we are performing a bulk action
        self.__is_bulk_action = False

        # message text to display
        self.__message = ""
        
        # token for detecting when to abort loading
        self.__token = 0
        
        self.__search_term = ""
        
        self.__tn_scheduler = ItemScheduler()
        
    
        ThumbableGridView.__init__(self)
        self.add_overlay_renderer(self.__render_message)
        #self.add_overlay_renderer(self.__render_search_box)
        #self.add_overlay_renderer(self.__render_caps)

        self.connect_item_shifted(self.__on_shift_item)


    def connect_folder_begin(self, cb, *args):
    
        self._connect(self.EVENT_FOLDER_BEGIN, cb, *args)


    def connect_folder_progress(self, cb, *args):
    
        self._connect(self.EVENT_FOLDER_PROGRESS, cb, *args)


    def connect_folder_complete(self, cb, *args):
    
        self._connect(self.EVENT_FOLDER_COMPLETE, cb, *args)


    def connect_file_opened(self, cb, *args):
    
        self._connect(self.EVENT_FILE_OPENED, cb, *args)


    def connect_file_enqueued(self, cb, *args):
    
        self._connect(self.EVENT_FILE_ENQUEUED, cb, *args)


    def connect_file_removed(self, cb, *args):
    
        self._connect(self.EVENT_FILE_REMOVED, cb, *args)


    def connect_file_bookmarked(self, cb, *args):
    
        self._connect(self.EVENT_FILE_BOOKMARKED, cb, *args)
        

    def connect_file_added_to_library(self, cb, *args):
    
        self._connect(self.EVENT_FILE_ADDED_TO_LIBRARY, cb, *args)


    def set_message(self, message):
        """
        Sets a message to display.
        
        @param message: the message to display
        """
    
        self.__message = message


    def __render_message(self, screen):

        if (not self.__message): return
            
        x, y = self.get_screen_pos()
        w, h = self.get_size()
       
        tw, th = text_extents(self.__message, theme.font_list_message)
        bw = tw + 20
        bh = th + 6
        tx = (w - bw) / 2 + (bw - tw) / 2
        ty = (h - bh) + (bh - th) / 2

        screen.fill_area((w - bw) / 2, h - bh,
                         bw, bh, theme.color_list_message_background)
        screen.draw_text(self.__message, theme.font_list_message, tx, ty,
                         theme.color_list_message)


    """
    def __render_search_box(self, screen):

        if (not self.__search_term): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
       
        tw, th = text_extents(self.__search_term, theme.font_mb_search_term)
        bh = th + 6
        screen.fill_area(0, 0, w, th + 6, theme.color_mb_list_letter_background)
        screen.draw_pixbuf(theme.mb_search, 4, (bh - 48) / 2)
        screen.draw_text(self.__search_term, theme.font_mb_search_term,
                         64, (bh - th) / 2,
                         theme.color_mb_list_letter)
    
    
    def __render_caps(self, screen):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        
        screen.draw_pixbuf(theme.mb_list_top, 0, 0, w, 32, True)
        screen.draw_pixbuf(theme.mb_list_bottom, 0, h - 32, w, 32, True)
    """
     

    def __on_item_clicked(self, item):

        f = item.get_file()
        
        def open_file():
            if (f.mimetype.endswith("-folder")):
                self.load_folder(f, self.GO_CHILD)
            else:
                self.send_event(self.EVENT_FILE_OPENED, f)

        gobject.timeout_add(0, open_file)


    def __on_item_menu_opened(self, item):
    
        cwd = self.get_current_folder()
        f = item.get_file()
        
        actions = cwd.get_file_actions(f)
        if (not actions):
            return
        
        dlg = OptionDialog("Actions")
        callbacks = []
        for icon, name, cb in actions:
            dlg.add_option(icon, name)
            callbacks.append(cb)

        if (dlg.run() != 0):
            return

        choice = dlg.get_choice()
        if (choice != -1):
            callbacks[choice](cwd, f)
            

    def __remove_item(self, idx):

        folder = self.get_current_folder()
        folder.delete_file(idx)


    def __on_shift_item(self, pos, amount):
    
        folder = self.get_current_folder()
        folder.shift_file(pos, amount)


    def __prerender_item(self):
        """
        Takes an item from the queue and prerenders it.
        """
        
        if (self.__items_to_prerender):
            item = self.__items_to_prerender.pop(0)
            #print "prerendering", item.get_name()
            item.render_at(None, 0, 0)
            return True
        else:
            self.__prerender_handler = None
            return False

        
    def set_root_device(self, device):
        """
        Sets the device used as the root.
        
        @param device: storage device
        """
        
        root = device.get_root()
        self.load_folder(root, self.GO_NEW)


    def get_path_stack(self):
        """
        Returns the path stack.
        """
        
        return [ p for p, s in self.__path_stack ]
        
        
    def set_path_stack(self, stack):
        """
        Loads a path stack.
        """
        
        self.__path_stack = [ [s, _STATUS_INVALID] for s in stack ]

        
    def begin_bulk_action(self):
        """
        Marks the beginning of a bulk action. Returns C{True} if an action
        was selected, C{False} otherwise.
        """

        cwd = self.get_current_folder()
        
        actions = cwd.get_bulk_actions()
        if (not actions):
            return False
        
        dlg = OptionDialog("Actions")
        callbacks = []
        for icon, name, cb in actions:
            dlg.add_option(icon, name)
            callbacks.append(cb)

        if (dlg.run() != 0):
            return False

        choice = dlg.get_choice()
        if (choice != -1):
            self.__bulk_action_handler = callbacks[choice]    
            self.set_multi_select(True)

            return True
        else:
            return False
            
        self.__is_bulk_operation = True
        
        
    def perform_bulk_action(self):
        """
        Performs the previously selected bulk action.
        """
        
        if (self.__bulk_action_handler):
            cwd = self.get_current_folder()
            selected = [ item.get_file() for item in self.get_items()
                         if item.is_selected() ]

            self.set_multi_select(False)
            if (selected):
                self.__bulk_action_handler(cwd, *selected)
            self.__bulk_action_handler = None        
        #end if
        
        
    def invalidate_folder(self, folder):
        """
        Marks the given folder as invalid. This forces a complete reload of
        the folder.
        
        @param folder: the folder to invalidate
        """
        
        found = False
        for entry in self.__path_stack:
            f, status = entry
            if (f == folder):
                entry[1] = _STATUS_INVALID
                found = True
        #end for
        
        if (found):
            self.reload_current_folder()
    
        
    def get_current_folder(self):
        """
        Returns the File object of the current folder, or None if the
        path is empty.
        
        @return: File object representing the current folder
        """
        
        path = self.get_path()
        if (path):
            return path[-1]
        else:
            return None
        
        
    def get_path(self):
        """
        Returns the elements of the current path as a list of File objects.
        
        @return: list of File objects
        """

        return [ p for p, nil in self.__path_stack ]
        
        
    def get_files(self):
        """
        Returns a list of files in the current folder.
        
        @return: list of File objects
        """
    
        return [ i.get_file() for i in self.get_items() ]


    def search(self, key, direction):
        """
        Searches for an item containing the given key, and returns its index,
        if available, or -1.
        
        @param key: string to search for
        @param direction: search direction,
                          -1 for backward search, 1 for forward search
        @return: index of the item
        """
    
        self.__search_term = key
        self.render()
        if (not key): return -1
    
        idx = self.get_cursor() - 1
        if (idx < 1): idx = 1
        current_idx = idx
        if (direction == -1):
            idx -= 1
        else:
            idx += 1

        files = self.get_files()
        l = len(files)
        while (idx != current_idx):
            if (idx >= l):
                idx = 0
            elif (idx < 0):
                idx = l - 1
                
            f = files[idx]
            #print idx, key, f
            if (key in f.name.lower()):
                logging.info("search: found '%s' for '%s'" % (f.name, key))
                return idx + 1

            if (direction == -1):
                idx -= 1
            else:
                idx += 1
        #end while
        
        return -1
        
        
    def hilight_file(self, f):
        """
        Hilights the given file and scrolls the list to that file.
        """
        
        self.__hilighted_file = f
        if (f):
            try:
                idx = self.get_files().index(f)
            except ValueError:
                idx = -1
        else:
            idx = -1
        
        self.set_hilight(idx)
        self.invalidate()
        if (idx != -1):
            self.scroll_to_item(idx)
        
        
    def move_cursor(self, direction, skip_letter):
        """
        Moves the cursor by one in the given direction. If C{skip_letter} is
        C{True}, the cursor skips to the next or previous letter, depending
        on C{direction}.
        @since: 0.97
        
        @param direction: C{-1} for moving backward or C{1} for moving forward
        @param skip_letter: whether to skip the current letter
        """
        
        cursor = self.get_cursor()
        letter = self.get_item(cursor).get_letter()
        l = len(self.get_items())
        while (self.get_item(cursor).get_letter() == letter):
            if (direction == -1):
                if (cursor > 0):
                    cursor -= 1
                else:
                    break
            elif (direction == 1):
                if (cursor + 1 < l):
                    cursor += 1
                else:
                    break
            #end if
            
            if (not skip_letter):
                break
            else:
                self.show_letter()
        #end while

        self.set_cursor(cursor)
        
        
    def go_root(self):
        """
        Goes all the way up to the root folder.
        """
        
        while (len(self.__path_stack) > 1):
            self.__path_stack.pop()
        self.reload_current_folder()

        
    def go_parent(self):
       
        if (len(self.__path_stack) > 1):
            self.__path_stack.pop()
            path, status = self.__path_stack.pop()
            if (status == _STATUS_INVALID):
                self.load_folder(path, self.GO_PARENT, True)
            else:
                self.load_folder(path, self.GO_PARENT, False)


    def reload_current_folder(self):
        """
        Reloads the current folder.
        """
        
        if (self.get_current_folder()):
            self.load_folder(self.get_current_folder(), self.GO_NEW)
        
        
    def load_folder(self, folder, direction, force_reload = False):
        """
        Loads the given folder and displays its contents.

        @param folder: File object of the folder to load
        @param direction: One of C{GO_NEW}, C{GO_CHILD}, or C{GO_PARENT}
        @param force_reload: whether to force reloading the folder
        """

        # are we just reloading the same folder?
        reload_only = False
        if (self.__path_stack):
            if (folder == self.get_current_folder()):
                reload_only = True
        #end if

        if (not reload_only):
            self.set_filter()

        # is a full reload required?
        if (reload_only):
            full_reload = True
        elif (force_reload):
            full_reload = True
        elif (direction == self.GO_NEW):
            full_reload = True
        elif (direction == self.GO_CHILD):
            full_reload = True
        elif (direction == self.GO_PARENT):
            full_reload = False
            #self.__path_stack[-1][1] = _STATUS_INVALID
        else:
            # what else..?
            full_reload = True

        # update path stack
        if (not reload_only):
            self.__path_stack.append([folder, _STATUS_INCOMPLETE])

        self.switch_item_set(folder.full_path)
        self.set_cursor(-1)
        self.emit_event(self.EVENT_FOLDER_BEGIN, folder)
        self.__items_to_prerender = []
        
        if (folder.folder_flags & folder.ITEMS_UNSORTED):
            self.set_letter_enabled(False)
        else:
            self.set_letter_enabled(True)
        
        if (full_reload):
            # reload list
            self.clear_items()
            self.invalidate()
            
        else:
            # don't reload list
            pass

        # animate
        if (direction == self.GO_CHILD):
            #self.fx_slide_left()
            pass
        elif (direction == self.GO_PARENT):
            #self.fx_slide_right()
            pass
        else:
            #self.render()
            pass
        self.render()

        # load remaining items
        loading_status = self.__path_stack[-1][1]
        if (loading_status == _STATUS_INCOMPLETE or full_reload):
            self.set_message("Loading")
            self.complete_current_folder()
        else:
            self.emit_event(self.EVENT_FOLDER_COMPLETE, folder)

        if (not self.__prerender_handler):
            self.__prerender_handler = gobject.idle_add(self.__prerender_item)

        # now is a good time to collect garbage
        #import gc; gc.collect()    
      
        
    def complete_current_folder(self):
        """
        Completes loading the current folder. Appends new elements to the
        current file list.
        """

        def on_child(f, token, path, entries):
            # abort if the user has changed the directory inbetween
            if (token != self.__token): return False

            if (f):
                #self.set_message("Loading") # (%d items)" % len(self.get_files()))
                entries.append(f)
                try:
                    self.__add_file(f)
                    self.emit_event(self.EVENT_FOLDER_PROGRESS,
                                    self.get_current_folder(), f)
                except:
                    print logging.stacktrace()

            else:
                message = self.get_current_folder().message
                if (message):
                    self.set_message(message)
                elif (len(self.get_files()) > 0):
                    self.set_message("")
                else:
                    self.set_message("Folder contains no media")
                
                # mark folder as complete
                self.__path_stack[-1][1] = _STATUS_OK
                
                self.invalidate()
                self.emit_event(self.EVENT_FOLDER_COMPLETE,
                                self.get_current_folder())

                # now is a good time to collect garbage
                import gc; gc.collect()    
            #end if

            # give visual feedback while loading the visible part of a folder
            if (len(entries) == 12 or not f): #not f or len(entries) == 12):
                self.invalidate()
                self.render()
                #while (gtk.events_pending()):
                #    gtk.main_iteration(False)
            #end if

            """
            # don't block UI while loading non-local folders
            t = int((time.time() - open_time) * 10)
            if (t % 2 == 0): #time.time() > open_time + 3):
                while (gtk.events_pending()):
                       gtk.main_iteration(False)
            """

            if (not f):
                # last item has been reached
                return False
            else:
                # continue loading next item
                return True


        cwd = self.get_current_folder()
        num_of_items = len(self.get_files())
        self.__token = (self.__token + 1) % 100
        open_time = time.time()
        cwd.get_contents(num_of_items, 0, on_child, self.__token, cwd, [])
        
        
    def __add_file(self, f):

        """
        Adds the given file item to the list.
        """

        cwd = self.get_current_folder()

        item = MediaItem(f, f.icon or "")
        item.connect_clicked(self.__on_item_clicked, item)
        item.connect_menu_opened(self.__on_item_menu_opened, item)

        # determine available item buttons
        buttons = []

        if (cwd.folder_flags & cwd.ITEMS_COMPACT):
            item.set_compact(True)        

        if (cwd.folder_flags & cwd.ITEMS_SORTABLE):
            item.set_draggable(True)
    
        self.append_item(item)

        l = len(self.get_items())
        idx = l - 1

        # hilight currently selected file
        if (self.__hilighted_file == f):
            self.set_hilight(idx)
        #self.invalidate_item(idx)

        # prerender some of the items now, some later; this should
        # distribute CPU load and disk IO
        #if (l % 3 == 0):
        #    item.render_at(None, 0, 0)
        #else:
        self.__items_to_prerender.append(item)

