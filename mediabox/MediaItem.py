from ui.itemview.Item import Item
from ui import pixbuftools
from theme import theme

import gtk
import os



class MediaItem(Item):

    EVENT_ACTIVATED = "activated"
    EVENT_MENU_OPENED = "menu-opened"

    # cache for thumbnails: path -> (mtime, pbuf)
    __thumbnail_cache = {}


    def __init__(self, f, icon):
       
        # whether this item is rendered compact
        self.__is_compact = False

        self.__file = f
        self.__icon = icon
        self.__label = f.name
        self.__letter = self.__label and unicode(self.__label)[0].upper() or " "
        self.__sublabel = f.info

        Item.__init__(self)
        self.set_size(-1, 100)


    def connect_activated(self, cb, *args):
    
        self._connect(self.EVENT_ACTIVATED, cb, *args)


    def connect_menu_opened(self, cb, *args):
    
        self._connect(self.EVENT_MENU_OPENED, cb, *args)


    def get_file(self):
    
        return self.__file


    def set_letter(self, letter):
    
        self.__letter = letter


    def get_letter(self):
    
        return self.__letter


    def set_icon(self, icon):
    
        self.__icon = icon
        self._invalidate_cached_pixmap()


    def has_icon(self):
    
        return self.__icon
    

    def set_info(self, info):
    
        self.__sublabel = info
        self._invalidate_cached_pixmap()
        
         
    def set_compact(self, v):
    
        self.__is_compact = v
        w, h = self.get_size()
        if (self.__is_compact): 
            self.set_size(w, 150)
            #self.__render_compact()
        else:
            self.set_size(w, 100)

        
    def render_at(self, cnv, x, y):

        w, h = self.get_size()
    
        if (self.__is_compact):
            pmap = self.__render_compact()
        else:
            pmap = self.__render_normal()

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)
    
            
    def __render_compact(self):
        """
        Compact rendering of the item.
        """

        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            # render selection frame
            if (self.is_marked()):
                pmap.fill_area(0, 0, w, h, "#00000040")
            
            elif (self.is_hilighted()):
                pmap.draw_frame(theme.mb_selection_frame,
                                4, 0, w - 8, h, True,
                                pmap.TOP | pmap.BOTTOM | pmap.LEFT | pmap.RIGHT)
           
            # render icon
            pbuf = self.__load_pixbuf(self.__icon)
            if (pbuf):
                #pmap.fit_pixbuf(pbuf, 4, 4, w - 8, h - 32)
                p_w = pbuf.get_width()
                pmap.draw_pixbuf(pbuf, (w - p_w) / 2, 4)
                #del pbuf

            # render text
            pmap.set_clip_rect(5, 0, w - 10, h)
            pmap.draw_centered_text(self.__label, theme.font_mb_plain,
                                    5, h - 26, w - 10, 26,
                                    theme.color_list_item_text)
            pmap.set_clip_rect()
            
        #end if
        
        return pmap

    
    def __render_normal(self):
        """
        Normal rendering of the item.
        """
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            # render selection frame
            if (self.is_marked()):
                pmap.fill_area(0, 0, w, h, "#00000040")
            
            elif (self.is_hilighted()):
                pmap.draw_frame(theme.mb_selection_frame, 0, 0, w, h, True,
                                pmap.TOP | pmap.BOTTOM | pmap.LEFT | pmap.RIGHT)

            # render grip
            if (self.is_draggable()):
                pmap.draw_pixbuf(theme.mb_item_grip, w - 32, (h - 80) / 2)
                clip_rect = (0, 0, w - 34, h)
            else:
                clip_rect = (0, 0, w, h)
            
            offset = 4
            
            # render icon
            pbuf = self.__load_pixbuf(self.__icon)
            if (pbuf):
                pmap.fit_pixbuf(pbuf, offset, 5, 120, h - 10)
                del pbuf
                            
            offset = 134
            
            # render text
            pmap.set_clip_rect(*clip_rect)
            pmap.draw_text(self.__label, theme.font_mb_plain,
                           offset, 12,
                           theme.color_list_item_text)
            pmap.draw_text(self.__sublabel, theme.font_mb_tiny,
                           offset, 40,
                           theme.color_list_item_subtext)
            pmap.set_clip_rect()
        #end if
        
        return pmap
        
           
    def tap_and_hold(self, px, py):
        """
        Handles tap-and-hold events.
        """
    
        self.emit_event(self.EVENT_MENU_OPENED)


    def _invalidate_cached_pixmap(self):
        """
        Invalidates the cached pixmap as well as the cached icon.
        """

        Item._invalidate_cached_pixmap(self)
        if (self.__icon in self.__thumbnail_cache):
            del self.__thumbnail_cache[self.__icon]


    def __trim_cache(self):
        """
        Trims the cache so that it doesn't grow indefinitely.
        """

        while (len(self.__thumbnail_cache) > 250):
            item = self.__thumbnail_cache.keys()[0]
            del self.__thumbnail_cache[item]
        #end while


    def __load_pixbuf(self, path):
        """
        Loads the icon pixbuf and its frame, if any.
        """

        # try to retrieve from icon cache
        if (path and path.startswith("/") and path in self.__thumbnail_cache):
            mtime, pbuf = self.__thumbnail_cache[path]
            if (os.path.getmtime(path) <= mtime):
                return pbuf
        #end if

        if (path):
            try:
                if (path.startswith("data://")):
                    import base64
                    data = base64.b64decode(path[7:])
                    loader = gtk.gdk.PixbufLoader()
                    loader.write(data)
                    loader.close()
                    icon = loader.get_pixbuf()
                    del loader
            
                else:
                    icon = gtk.gdk.pixbuf_new_from_file(path)

            except:
                import traceback; traceback.print_exc()
                icon = None

        else:
            icon = None

        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 160, 120)
        pbuf.fill(0x00000000)
        
        frm, x, y, w, h = self.__file.frame
        if (frm):
            pixbuftools.draw_pbuf(pbuf, frm, 0, 0)
        else:
            x, y, w, h = 0, 0, 160, 120
        if (icon):            
            pixbuftools.fit_pbuf(pbuf, icon, x, y, w, h)
            del icon

        self.__trim_cache()
        if (path and path.startswith("/")):
            self.__thumbnail_cache[path] = (os.path.getmtime(path), pbuf)

        return pbuf

