from MediaItem import MediaItem
from ui.itemview.ThumbableGridView import ThumbableGridView
from ui.dialog import OptionDialog
from ui.Pixmap import text_extents
from theme import theme
from utils.ItemScheduler import ItemScheduler
from utils import logging

import time
import gobject


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

        # timestamp of the last list rendering
        self.__last_list_render_time = 0
              
        # the currently hilighted file
        self.__hilighted_file = None
        
        # whether we are performing a bulk operation
        self.__is_bulk_operation = False

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
        


    def trigger_item_button(self, idx):
    
        item = self.get_items()[idx]
        button = item.BUTTON_PLAY
        self.__on_item_button(item, idx, button)


    def __on_item_clicked(self, item):
    
        #idx = self.get_items().index(item)
    
        #self.set_cursor(idx)
        #self.set_hilight(idx)
        #self.invalidate_item(idx)
        #self.invalidate()
        #self.render()

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
        
        dlg = OptionDialog("Options")
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

        
    def set_root_device(self, device):
        """
        Sets the device used as the root.
        
        @param device: storage device
        """
        
        root = device.get_root()
        gobject.idle_add(self.load_folder, root, self.GO_NEW)
              
        
    def begin_bulk_operation(self):
        """
        Marks the beginning of a bulk operation.
        Invalidated folder don't get reloaded while a bulk operation is in
        progress.
        """
    
        self.__is_bulk_operation = True
        
        
    def end_bulk_operation(self):
        """
        Marks the end of a bulk operation.
        """
        
        self.__is_bulk_operation = False
        self.reload_current_folder()
        
        
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
        
        if (found and not self.__is_bulk_operation):
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
        
        if (full_reload):
            # reload list
            self.clear_items()

            #header = HeaderItem(folder.name)
            #header.set_info("Retrieving...")
            #buttons = []
            #if (folder.folder_flags & folder.ITEMS_ENQUEUEABLE):
            #    buttons.append((header.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))
            #if (folder.folder_flags & folder.INDEXABLE):
            #    buttons.append((header.BUTTON_ADD_TO_LIBRARY, theme.mb_item_btn_add))
            #header.set_buttons(*buttons)
            
        else:
            # don't reload list
            pass

        # animate
        if (direction == self.GO_CHILD):
            self.fx_slide_left()
        elif (direction == self.GO_PARENT):
            self.fx_slide_right()
        else:
            #self.render()
            pass

        # load remaining items
        loading_status = self.__path_stack[-1][1]
        if (loading_status == _STATUS_INCOMPLETE or full_reload):
            #self.set_message("Loading")
            self.complete_current_folder()
        else:
            self.emit_event(self.EVENT_FOLDER_COMPLETE, folder)

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
                #self.get_item(0).set_info("%d items" \
                #                          % len(self.get_files()))
                #self.set_message("Loading") # (%d items)" % len(self.get_files()))
                #self.invalidate_item(0)
                entries.append(f)
                try:
                    self.__add_file(f)
                    self.emit_event(self.EVENT_FOLDER_PROGRESS,
                                    self.get_current_folder(), f)
                except:
                    print logging.stacktrace()

            else:
                #self.get_item(0).set_info("%d items" % len(self.get_files()))
                #self.invalidate_item(0)
                if (len(self.get_files()) > 0):
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
            if (not f or len(entries) in (4, 8, 12, 16)):
                    self.invalidate()
                    self.render()
            #end if

            # don't block UI while loading non-local folders
            import gtk
            now = time.time()
            if (gtk.events_pending() or 
                now > self.__last_list_render_time + 0.5):
           
                self.__last_list_render_time = now

                while (f and not f.is_local and gtk.events_pending()):
                    gtk.main_iteration(False)
            #end if

            if (not f):
                # last item has been reached
                print "FINISHED"
                return False
            else:
                # continue loading next item
                return True


        cwd = self.get_current_folder()
        num_of_items = len(self.get_files())
        self.__token = (self.__token + 1) % 100
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

        idx = len(self.get_items()) - 1

        #if (not cwd.folder_flags & cwd.ITEMS_SORTED_ALPHA):
        #    item.set_letter(`idx + 1`)

        # hilight currently selected file
        if (self.__hilighted_file == f):
            self.set_hilight(idx)
        self.invalidate_item(idx)
