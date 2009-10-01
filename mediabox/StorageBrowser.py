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
    
    EVENT_FOLDER_OPENED = "folder-opened"
    
    EVENT_FILE_OPENED = "file-opened"
    EVENT_FILE_ENQUEUED = "file-enqueued"
    EVENT_FILE_REMOVED = "file-removed"
    EVENT_FILE_BOOKMARKED = "file-bookmarked"
    EVENT_FILE_ADDED_TO_LIBRARY = "file-added-to-library"
    EVENT_THUMBNAIL_REQUESTED = "thumbnail-requested"
    

    def __init__(self):

        # list of tuples: (path, status)
        self.__path_stack = []

        # timestamp of the last list rendering
        self.__last_list_render_time = 0

        # range of subfolder, if any
        self.__subfolder_range = None
        
        # callback for loading thumbnails
        self.__thumbnailer = lambda *f:None
        
        # the currently hilighted file
        self.__hilighted_file = None
        
        # whether we are performing a bulk operation
        self.__is_bulk_operation = False

        # message text to display
        self.__message = ""
        
        self.__search_term = ""
        
        self.__tn_scheduler = ItemScheduler()
        
    
        ThumbableGridView.__init__(self)
        self.add_overlay_renderer(self.__render_message)
        self.add_overlay_renderer(self.__render_search_box)
        self.add_overlay_renderer(self.__render_caps)
        self.set_background(theme.color_mb_background)

        #self.connect_item_clicked(self.__on_item_clicked)
        #self.connect_button_clicked(self.__on_item_button)


    def set_size(self, w, h):
    
        ThumbableGridView.set_size(self, w, h)
        #for item in self.get_items():
        #    item.set_size(w, 100)


    def connect_folder_opened(self, cb, *args):
    
        self._connect(self.EVENT_FOLDER_OPENED, cb, *args)


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


    def connect_thumbnail_requested(self, cb, *args):
    
        self._connect(self.EVENT_THUMBNAIL_REQUESTED, cb, *args)


    def _visibility_changed(self):
    
        if (self.is_visible()):
            self.__tn_scheduler.resume()
        else:
            self.__tn_scheduler.halt()


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
       
        tw, th = text_extents(self.__message, theme.font_mb_listitem)
        bw = tw + 20
        bh = th + 6
        tx = (w - bw) / 2 + (bw - tw) / 2
        ty = (h - bh) + (bh - th) / 2

        screen.fill_area((w - bw) / 2, h - bh,
                         bw, bh, theme.color_mb_list_letter_background)
        screen.draw_text(self.__message, theme.font_mb_listitem, tx, ty,
                         theme.color_mb_list_letter)


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
    
        idx = self.get_items().index(item)
    
        self.set_cursor(idx)
        self.set_hilight(idx)
        #self.invalidate_item(idx)
        self.invalidate()
        self.render()

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
        idx = self.get_items().index(item)
    
        options = []

        if (not f.bookmarked):
            options.append((None, "Add to Favorites",
                            self.EVENT_FILE_BOOKMARKED))
    
        if (cwd.folder_flags & cwd.ITEMS_ENQUEUEABLE):
            options.append((None, "Add to Playlist",
                            self.EVENT_FILE_ENQUEUED))

        if (f.folder_flags & f.INDEXABLE):
            options.append((None, "Add to Library",
                            self.EVENT_FILE_ADDED_TO_LIBRARY))

        if (cwd.folder_flags & cwd.ITEMS_DELETABLE):
            options.append((None, "Delete",
                            self.EVENT_FILE_REMOVED))

        if (not options):
            return
            
        dlg = OptionDialog("Options")
        for icon, label, ev in options:
            dlg.add_option(icon, label)
            
        if (dlg.run() != 0):
            return

        choice = dlg.get_choice()
        if (choice != -1):
            ev = options[choice][2]

            if (ev == self.EVENT_FILE_ENQUEUED):
                pass
            
            elif (ev == self.EVENT_FILE_REMOVED):
                self.__remove_item(idx)
            
            self.emit_event(ev, f)
        #end if



    """
    def __on_item_button_pressed(self, button, item):
    
        idx = self.get_items().index(item)

        print "BUTTON", button, idx
        if (button == item.BUTTON_PLAY):
            f = item.get_file()
            self.set_hilight(idx)
            self.render()
            if (f.mimetype.endswith("-folder")):
                self.load_folder(f, self.GO_CHILD)
            else:
                self.send_event(self.EVENT_FILE_OPENED, f)

        elif (button == item.BUTTON_OPEN):
            print "OPEN"
            f = item.get_file()
            self.insert_folder(f)


        
    def __on_item_button(self, item, idx, button):

        if (idx == -1): return
        
        if (button == item.BUTTON_PLAY):
            f = item.get_file()
            self.set_hilight(idx)
            self.render()
            if (f.mimetype.endswith("-folder")):
                self.load_folder(f, self.GO_CHILD)
            else:
                self.send_event(self.EVENT_FILE_OPENED, f)

        elif (button == item.BUTTON_OPEN):
            f = item.get_file()
            self.insert_folder(f)

        elif (button == item.BUTTON_ENQUEUE):
            if (idx == 0):
                f = self.get_current_folder()
            else:
                f = item.get_file()
            self.send_event(self.EVENT_FILE_ENQUEUED, f)

        elif (button == item.BUTTON_REMOVE):
            self.__remove_item(idx - 1)

        elif (button == item.BUTTON_REMOVE_PRECEDING):
            a = 0
            b = idx - 1
            self.begin_bulk_operation()
            print a, b, len(range(a, b + 1))
            for i in range(a, b + 1):
                self.__remove_item(0)
            self.end_bulk_operation()

        elif (button == item.BUTTON_REMOVE_SUCCEEDING):
            a = idx - 1
            b = len(self.get_items()) - 1 - 1
            self.begin_bulk_operation()
            for i in range(a, b + 1):
                self.__remove_item(a)
            self.end_bulk_operation()

        elif (button == item.BUTTON_ADD_TO_LIBRARY):
            f = self.get_current_folder()
            self.send_event(self.EVENT_FILE_ADDED_TO_LIBRARY, f)
    """

    def __remove_item(self, idx):

        folder = self.get_current_folder()
        folder.delete_file(idx)


    """
    def __on_swap_items(self, idx1, idx2):
    
        folder = self.get_current_folder()
        if (folder):
            # -1 because there's a header item
            folder.swap(idx1 - 1, idx2 - 1)
    """

        
    def set_root_device(self, device):
        """
        Sets the device used as the root.
        
        @param device: storage device
        """
        
        root = device.get_root()
        gobject.idle_add(self.load_folder, root, self.GO_NEW)
        
        
    def set_thumbnailer(self, cb):
        """
        Sets a callback function for providing thumbnails.
        
        Signature of the callback: C{(f, cb, *args)}
        
        @param cb: callback function
        """
    
        self.__thumbnailer = cb
        
        
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
        
        #if (self.__path_stack and self.__path_stack[-1][1] == _STATUS_INVALID):
        #    self.reload_current_folder()
        if (found and not self.__is_bulk_operation):
            self.reload_current_folder()
    
        
    def get_current_folder(self):
        """
        Returns the File object of the current folder, or None if there the
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
    
        if (self.__subfolder_range):
            self.__close_subfolder()
        
        elif (len(self.__path_stack) > 1):
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
        
        self.load_folder(self.get_current_folder(), self.GO_PARENT)  
        
        
    def load_folder(self, folder, direction, force_reload = False):
        """
        Loads the given folder and displays its contents.

        @param folder: File object of the folder to load
        @param direction: One of C{GO_NEW}, C{GO_CHILD}, or C{GO_PARENT}
        @param force_reload: whether to force reloading the folder
        """

        #self.__close_subfolder()
        #self.__tn_scheduler.new_schedule(5, self.__on_load_thumbnail)
        #self.__tn_scheduler.halt()

        self.emit_event(self.EVENT_FOLDER_BEGIN, folder)

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

        if (folder.folder_flags & folder.ITEMS_COMPACT):
            self.set_items_per_row(3)
        else:
            self.set_items_per_row(1)

        if (full_reload):
            # reload list
            self.switch_item_set(folder.full_path)
            self.clear_items()

            #header = HeaderItem(folder.name)
            #header.set_info("Retrieving...")
            #buttons = []
            #if (folder.folder_flags & folder.ITEMS_ENQUEUEABLE):
            #    buttons.append((header.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))
            #if (folder.folder_flags & folder.INDEXABLE):
            #    buttons.append((header.BUTTON_ADD_TO_LIBRARY, theme.mb_item_btn_add))
            #header.set_buttons(*buttons)
            
            if (folder.folder_flags & folder.ITEMS_SORTABLE):
                self.set_drag_sort_enabled(True)
            else:
                self.set_drag_sort_enabled(False)

            #self.append_item(header)

        else:
            # don't reload list
            #self.clear_items()
            self.switch_item_set(folder.full_path)
            #self.set_hilight(-1)
            
        #w, h = self.get_size()
        #for item in self.get_items():
        #    item.set_size(w, 100)

        # animate
        if (direction == self.GO_CHILD):
            self.fx_slide_left()
        elif (direction == self.GO_PARENT):
            self.fx_slide_right()
        else:
            self.render()

        # load remaining items
        loading_status = self.__path_stack[-1][1]
        if (loading_status == _STATUS_INCOMPLETE or full_reload):
            self.set_message("Loading")
            self.complete_current_folder()
        else:
            self.emit_event(self.EVENT_FOLDER_COMPLETE, folder)

        # now is a good time to collect garbage
        import gc; gc.collect()    

   
    """     
    def __close_subfolder(self):

        if (not self.__subfolder_range): return
        
        idx1, idx2 = self.__subfolder_range
        n = idx2 - idx1
        for i in range(n):
            self.remove_item(idx1 + 1)
        #end for
        
        item = self.get_item(idx1)
        #item.set_buttons((item.BUTTON_OPEN, theme.mb_item_btn_open))
        
        self.__subfolder_range = None
        self.render()
    """
        
        
    def complete_current_folder(self):
        """
        Completes loading the current folder. Appends new elements to the
        current file list.
        """

        def on_child(f, path, entries):
            # abort if the user has changed the directory inbetween
            if (self.get_current_folder() != path): return False
            
            if (f):
                #self.get_item(0).set_info("%d items" \
                #                          % len(self.get_files()))
                self.set_message("Loading (%d items)" % len(self.get_files()))
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
                self.set_message("")
                
                # mark folder as complete
                self.__path_stack[-1][1] = _STATUS_OK
                
                # finished loading items; now create thumbnails
                #self.__tn_scheduler.resume()
                
                self.invalidate()
                self.render()
                self.emit_event(self.EVENT_FOLDER_COMPLETE,
                                self.get_current_folder())
                #self.send_event(self.EVENT_FOLDER_OPENED,
                #                self.get_current_folder())

            now = time.time()
            if (not f or now > self.__last_list_render_time + 1.0):
                self.__last_list_render_time = now
                #self.invalidate_buffer()
                self.render()
                
                if (not f):
                    return False
            
            return True


        cwd = self.get_current_folder()
        num_of_items = len(self.get_files())
        cwd.get_contents(num_of_items, 0, on_child, cwd, [])
        
        
    def __add_file(self, f):

        """
        Adds the given file item to the list.
        """

        cwd = self.get_current_folder()
        self.__support_legacy_folder_flags(cwd, f)

        #thumbnail = f.icon or ""
        item = MediaItem(f, f.icon or "")
        #if (not thumbnail):
        #    self.emit_event(self.EVENT_THUMBNAIL_REQUESTED, f, False,
        #             lambda thumbpath:self.__update_thumbnail(item, thumbpath))
        ##end if

        # remember for thumbnailing if no thumbnail was found
        #if (not item.has_icon() and f.mimetype != f.DIRECTORY):
        #    self.__tn_scheduler.add(item, f)

        #w, h = self.get_size()
        #item.set_size(w, 100)
        item.connect_activated(self.__on_item_clicked, item)
        item.connect_menu_opened(self.__on_item_menu_opened, item)

        # determine available item buttons
        buttons = []

        if (cwd.folder_flags & cwd.ITEMS_COMPACT):
            item.set_compact(True)        

        """
        if (f.mimetype in ("application/x-bookmarks-folder",
                           "application/x-music-folder")):
            buttons.append((item.BUTTON_OPEN, theme.mb_item_btn_open))
            
        elif (f.mimetype.endswith("-folder")):
            buttons.append((item.BUTTON_PLAY, theme.mb_item_btn_open))
            
        else:
            buttons.append((item.BUTTON_PLAY, theme.mb_item_btn_play))
            
            if (cwd.folder_flags & cwd.ITEMS_ENQUEUEABLE):
                buttons.append((item.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))
        #end if
            
        if (cwd.folder_flags & cwd.ITEMS_DELETABLE):
            buttons.append((item.BUTTON_REMOVE, theme.mb_item_btn_remove))

        if (cwd.folder_flags & cwd.ITEMS_BULK_DELETABLE):
            buttons.append((item.BUTTON_REMOVE_PRECEDING, theme.mb_item_btn_remove_up))
            buttons.append((item.BUTTON_REMOVE_SUCCEEDING, theme.mb_item_btn_remove_down))
        """

        #item.set_buttons(*buttons)
        #item.connect_button_pressed(self.__on_item_button_pressed, item)

        if (cwd.folder_flags & cwd.ITEMS_SORTABLE):
            item.set_grip_visible(True)
        else:
            item.set_grip_visible(False)
    
        self.append_item(item)


        idx = len(self.get_items()) - 1

        #if (not cwd.folder_flags & cwd.ITEMS_SORTED_ALPHA):
        #    item.set_letter(`idx + 1`)

        # hilight currently selected file
        if (self.__hilighted_file == f):
            self.set_hilight(idx)
        self.invalidate_item(idx)
        self.render()            

        import gtk
        cnt = 0
        while (gtk.events_pending() and cnt < 10):
            gtk.main_iteration(False)
            cnt += 1


    def __update_thumbnail(self, item, thumbpath):
    
        item.set_icon(thumbpath)
        #idx = self.get_items().index(item)
        # TODO: only render if item is currently on screen
        self.invalidate()
        self.render()


    def __on_load_thumbnail(self, item, f):

        def on_loaded(thumbpath):
            self.__update_thumbnail(item, thumbpath)
            
            if (self.is_visible()):
                self.__tn_scheduler.resume()
    
        # load thumbnail
        #self.set_message("Creating preview (%d of %d)" \
        #                    % (total - len(items_to_thumbnail), total))
        
        self.__tn_scheduler.halt()
        self.emit_event(self.EVENT_THUMBNAIL_REQUESTED, f, True, on_loaded)
        #self.__thumbnailer(f, on_loaded, item)


    def __support_legacy_folder_flags(self, folder, f):
        """
        Translates the legacy flags to the new folder flags.
        """
        
        if (folder.can_skip):
            folder.folder_flags |= folder.ITEMS_SKIPPABLE
            
        if (folder.can_add_to_library):
            folder.folder_flags |= folder.INDEXABLE

        if (folder.can_add):
            folder.folder_flags |= folder.ITEMS_ADDABLE

        if (not f): return
        
        if (f.can_delete):
            folder.folder_flags |= folder.ITEMS_DELETABLE

        if (f.can_keep):
            folder.folder_flags |= folder.ITEMS_DOWNLOADABLE

        if (f.can_download):
            folder.folder_flags |= folder.ITEMS_DOWNLOADABLE

