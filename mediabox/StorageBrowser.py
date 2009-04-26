from mediabox.TrackList import TrackList
from HeaderItem import HeaderItem
from MediaItem import MediaItem
from SubItem import SubItem
from theme import theme
from utils import logging

import time
import gobject


_STATUS_OK = 0
_STATUS_INCOMPLETE = 1
_STATUS_INVALID = 2


class StorageBrowser(TrackList):

    GO_NEW = 0
    GO_CHILD = 1
    GO_PARENT = 2
    
    EVENT_FOLDER_OPENED = "folder-opened"
    EVENT_FILE_OPENED = "file-opened"
    EVENT_FILE_ENQUEUED = "file-enqueued"
    EVENT_FILE_REMOVED = "file-removed"
    EVENT_FILE_ADDED_TO_LIBRARY = "file-added-to-library"
    

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

    
        TrackList.__init__(self, True)
        self.connect_button_clicked(self.__on_item_button)
        self.connect_items_swapped(self.__on_swap_items)


    def connect_folder_opened(self, cb, *args):
    
        self._connect(self.EVENT_FOLDER_OPENED, cb, *args)
        
        
    def connect_file_opened(self, cb, *args):
    
        self._connect(self.EVENT_FILE_OPENED, cb, *args)


    def connect_file_enqueued(self, cb, *args):
    
        self._connect(self.EVENT_FILE_ENQUEUED, cb, *args)


    def connect_file_removed(self, cb, *args):
    
        self._connect(self.EVENT_FILE_REMOVED, cb, *args)


    def connect_file_added_to_library(self, cb, *args):
    
        self._connect(self.EVENT_FILE_ADDED_TO_LIBRARY, cb, *args)


    def trigger_item_button(self, idx):
    
        item = self.get_items()[idx]
        button = item.BUTTON_PLAY
        self.__on_item_button(item, idx, button)

        
    def __on_item_button(self, item, idx, button):

        if (idx == -1): return
        
        if (button == item.BUTTON_PLAY):
            f = item.get_file()
            if (f.mimetype.endswith("-folder")):
                self.hilight(idx)
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
            f = item.get_file()
            print item.get_file()
            folder = self.get_current_folder()
            # support legacy plugins
            folder._LEGACY_SUPPORT_file_to_delete = f
            folder.delete_file(idx - 1)
            #self.reload_current_folder()
            self.send_event(self.EVENT_FILE_REMOVED, f)

        #elif (button == item.BUTTON_REMOVE_PRECEDING):
        #    pass

        #elif (button == item.BUTTON_REMOVE_SUCCEEDING):
        #    pass

        elif (button == item.BUTTON_ADD_TO_LIBRARY):
            f = self.get_current_folder()
            self.send_event(self.EVENT_FILE_ADDED_TO_LIBRARY, f)


    def __on_swap_items(self, idx1, idx2):
    
        folder = self.get_current_folder()
        if (folder):
            # -1 because there's a header item
            folder.swap(idx1 - 1, idx2 - 1)
        
        
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
        if (found):
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
    
        return [ i.get_file() for i in self.get_items()[1:] ]


    def search(self, key, direction):
        """
        Searches for an item containing the given key, and returns its index,
        if available, or -1.
        
        @param key: string to search for
        @param direction: search direction,
                          -1 for backward search, 1 for forward search
        @return: index of the item
        """
    
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
                idx = self.get_files().index(f) + 1
            except ValueError:
                idx = -1
        else:
            idx = -1
        
        self.hilight(idx)
        if (idx != -1):
            self.scroll_to_item(idx)
        
        
        
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
        
        self.load_folder(self.get_current_folder(), self.GO_NEW)  
        
        
    def load_folder(self, folder, direction, force_reload = False):
        """
        Loads the given folder and displays its contents.

        @param folder: File object of the folder to load
        @param direction: One of C{GO_NEW}, C{GO_CHILD}, or C{GO_PARENT}
        @param force_reload: whether to force reloading the folder
        """

        self.__close_subfolder()

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
        else:
            # what else..?
            full_reload = True

        # update path stack
        if (not reload_only):
            self.__path_stack.append([folder, _STATUS_INCOMPLETE])

        if (full_reload):
            # reload list
            self.change_image_set(folder.full_path)
            self.clear_items()

            header = HeaderItem(folder.name)
            header.set_info("Retrieving...")
            buttons = []
            if (folder.folder_flags & folder.ITEMS_ENQUEUEABLE):
                buttons.append((header.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))
            if (folder.folder_flags & folder.INDEXABLE):
                buttons.append((header.BUTTON_ADD_TO_LIBRARY, theme.mb_item_btn_add))
            header.set_buttons(*buttons)
            
            if (folder.folder_flags & folder.ITEMS_SORTABLE):
                self.set_drag_sort_enabled(True)
            else:
                self.set_drag_sort_enabled(False)

            self.append_item(header)

        else:
            # don't reload list
            self.clear_items()
            self.change_image_set(folder.full_path)
            self.hilight(-1)

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

        # now is a good time to collect garbage
        import gc; gc.collect()    


    def insert_folder(self, folder):

        def on_child(f, path, entries, items_to_thumbnail, insert_at):
            # abort if the user has changed the directory again
            if (self.get_current_folder() != path): return False

            if (f):
                self.__add_file(f, items_to_thumbnail, insert_at + len(entries))
                entries.append(f)

            else:
                # finished loading items; now create thumbnails
                #self.__create_thumbnails(path, items_to_thumbnail)
            
                self.send_event(self.EVENT_FOLDER_OPENED, folder)

            now = time.time()
            self.__subfolder_range = (insert_at, insert_at + len(entries))
            if (not f or now > self.__last_list_render_time + 1.0):
                self.__last_list_render_time = now
                #self.invalidate_buffer()
                self.render()
            
            return True
    
    
        self.__close_subfolder()
        idx = self.get_files().index(folder)
    
        # change item button
        item = self.get_item(idx + 1)
        if (folder.folder_flags & folder.ITEMS_ENQUEUEABLE):
            item.set_buttons(#(item.BUTTON_CLOSE, theme.mb_item_btn_close),
                             (item.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))

        folder.get_contents(0, 0, on_child, self.get_current_folder(), [], [],
                            idx + 1)
        
        
    def __close_subfolder(self):

        if (not self.__subfolder_range): return
        
        idx1, idx2 = self.__subfolder_range
        n = idx2 - idx1
        for i in range(n):
            self.remove_item(idx1 + 1)
        #end for
        
        item = self.get_item(idx1)
        item.set_buttons((item.BUTTON_OPEN, theme.mb_item_btn_open))
        
        self.__subfolder_range = None
        self.render()
        
        
    def complete_current_folder(self):
        """
        Completes loading the current folder. Appends new elements to the
        current file list.
        """

        def on_child(f, path, entries, items_to_thumbnail):
            # abort if the user has changed the directory inbetween
            if (self.get_current_folder() != path): return False
            
            if (f):
                self.get_item(0).set_info("Loading (%d items)..." \
                                          % len(self.get_files()))
                self.invalidate_image(0)
                entries.append(f)
                self.__add_file(f, items_to_thumbnail, -1)

            else:
                self.get_item(0).set_info("%d items" % len(self.get_files()))
                self.invalidate_image(0)
                self.set_message("")
                
                # mark folder as complete
                self.__path_stack[-1][1] = _STATUS_OK
                
                # finished loading items; now create thumbnails
                if (items_to_thumbnail):
                    self.set_message("Creating thumbnails")
                    self.__create_thumbnails(path, items_to_thumbnail)
                
                self.send_event(self.EVENT_FOLDER_OPENED,
                                self.get_current_folder())

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
        cwd.get_contents(num_of_items, 0, on_child, cwd, [], [])
        
        
    def __add_file(self, f, items_to_thumbnail, insert_at):

        """
        Adds the given file item to the list.
        """

        if (insert_at == -1):
            # look if there's a thumbnail available
            if (f.icon):
                thumbnail = f.icon
            else:
                thumbnail = self.__thumbnailer(f, None)

            item = MediaItem(f, thumbnail)
            # remember for thumbnailing if no thumbnail was found
            if (not thumbnail and f.mimetype != f.DIRECTORY):
                items_to_thumbnail.append((item, None, f))

        else:
            item = SubItem(f)

        # determine available item buttons
        buttons = []
        
        cwd = self.get_current_folder()
        self.__support_legacy_folder_flags(cwd, f)

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


        item.set_buttons(*buttons)

        if (insert_at == -1):
            if (cwd.folder_flags & cwd.ITEMS_SORTABLE):
                item.set_grip_visible(True)
            else:
                item.set_grip_visible(False)
        
            self.append_item(item)

        else:
            self.insert_item(item, insert_at)
            
        # hilight currently selected file
        if (self.__hilighted_file == f):
            idx = len(self.get_items())
            self.hilight(idx - 1)

        import gtk
        cnt = 0
        while (gtk.events_pending() and cnt < 10):
            gtk.main_iteration(False)
            cnt += 1


    def __create_thumbnails(self, folder, items_to_thumbnail):
        """
        Creates thumbnails for the given items.
        """

        def on_loaded(thumbpath, item, tn):
            if (item):
                item.set_icon(thumbpath)
                item.invalidate()
                self.invalidate_buffer()
                self.render()
            
            if (tn):
                tn.set_thumbnail(thumbpath)
                tn.invalidate()
            
            # proceed to next thumbnail
            gobject.idle_add(self.__create_thumbnails, folder,
                             items_to_thumbnail)
            

        # abort if the user has changed the directory inbetween
        if (self.get_current_folder() != folder): return
        
        if (not self.is_visible()): return
    
        if (items_to_thumbnail):
            # hmm, may we want to reorder a bit?
            if (len(items_to_thumbnail) % 10 == 0 and \
                  len(items_to_thumbnail) > 5):
                idx_in_list = self.get_index_at(0) - 1
                item_in_view = self.get_files()[idx_in_list]
                cnt = 0
                for i in items_to_thumbnail:
                    if (i[2] == item_in_view):
                        items_to_thumbnail = \
                                items_to_thumbnail[cnt:cnt + 5] + \
                                items_to_thumbnail[:cnt] + \
                                items_to_thumbnail[cnt + 5:]
                        break
                    cnt += 1 
                #end for
            #end if            
        
            item, tn, f = items_to_thumbnail.pop(0)

            # load thumbnail
            self.__thumbnailer(f, on_loaded, item, None)
            
        else:
            self.set_message("")
            self.render()
        #end if


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

