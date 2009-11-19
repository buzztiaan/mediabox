from ui.itemview.Item import Item
from mediabox import thumbnail
from utils import textutils
from theme import theme

import gtk


class MediaItem(Item):

    EVENT_ACTIVATED = "activated"
    EVENT_MENU_OPENED = "menu-opened"


    def __init__(self, f, icon):

        self.__grip_visible = False
        
        # whether this item is rendered compact
        self.__is_compact = False

        self.__file = f
        self.__icon = icon
        self.__label = f.name #textutils.escape_xml(f.name)
        self.__letter = self.__label and unicode(self.__label)[0].upper() or " "
        self.__sublabel = f.info #textutils.escape_xml(f.info)

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
        
         
    def set_grip_visible(self, v):
        
        self.__grip_visible = v
        self._invalidate_cached_pixmap()
        

    def set_compact(self, v):
    
        self.__is_compact = v
        w, h = self.get_size()
        if (self.__is_compact):
            self.set_size(w, 140)
        else:
            self.set_size(w, 100)

        

    def render_at(self, cnv, x, y):
    
        if (self.__is_compact):
            self.__render_compact(cnv, x, y)
        else:
            self.__render_normal(cnv, x, y)
            
            
    def __render_compact(self, cnv, x, y):

        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            # render selection frame
            if (self.is_marked()):
                pmap.fill_area(0, 0, w, h, "#ffffff60")

            elif (self.is_hilighted()):
                pmap.draw_frame(theme.mb_selection_frame,
                                4, 0, w - 8, h, True,
                                pmap.TOP | pmap.BOTTOM | pmap.LEFT | pmap.RIGHT)
           
            # render icon
            try:
                pbuf = gtk.gdk.pixbuf_new_from_file(self.__icon)
            except:
                pass
            else:
                pmap.fit_pixbuf(pbuf, 0, 0, w, h - 20)
                del pbuf

            #pbuf = thumbnail.render_on_pixbuf(self.__icon, self.__file.mimetype)
            ## weird, Fremantle requires me to make a copy of the pixbuf...
            #pbuf2 = pbuf.copy()
            #pmap.fit_pixbuf(pbuf2, 0, 0, w, h)
            #del pbuf2

            # render fav star
            #if (self.__file.bookmarked):
            #    icon = theme.mb_item_fav_2
            #else:
            #    icon = theme.mb_item_fav_1
            #pmap.draw_pixbuf(icon, 10, 10)

            # render text
            pmap.set_clip_rect(5, 0, w - 10, h)
            pmap.draw_centered_text(self.__label, theme.font_mb_listitem,
                                    5, h - 20, w - 10, 20,
                                    theme.color_mb_listitem_text)
            pmap.set_clip_rect()
            
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)

            
    
    def __render_normal(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        
        if (is_new):
            #print "FULL RENDER", self.__label

            #if (self.is_marked()):
            #    pmap.fill_area(0, 0, w, h, "#ff0000")
            #if (self.is_hilighted()):
            #    pmap.fill_area(0, 0, w, h, "#0000ff")
            #else:
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            # render selection frame
            if (self.is_marked()):
                pmap.fill_area(0, 0, w, h, "#ffffff60")
            
            elif (self.is_hilighted()):
                pmap.draw_frame(theme.mb_selection_frame, 0, 0, w, h, True,
                                pmap.TOP | pmap.BOTTOM | pmap.LEFT | pmap.RIGHT)

            # render grip
            if (self.__grip_visible):
                pmap.draw_pixbuf(theme.mb_item_grip, 0, 0)
                offset = 32
            else:
                offset = 4
            
            # render icon
            try:
                pbuf = gtk.gdk.pixbuf_new_from_file(self.__icon)
            except:
                pass
            else:
                pmap.fit_pixbuf(pbuf, offset, 5, 120, h - 10)
                del pbuf
                
            #pbuf = thumbnail.render_on_pixbuf(self.__icon, self.__file.mimetype)
            ## weird, Fremantle requires me to make a copy of the pixbuf...
            #pbuf2 = pbuf.copy()
            #pmap.fit_pixbuf(pbuf2, offset, 5, 120, h - 10)
            #del pbuf2

            # render fav star
            #if (self.__file.bookmarked):
            #    icon = theme.mb_item_fav_2
            #else:
            #    icon = theme.mb_item_fav_1
            #pmap.draw_pixbuf(icon, offset, 0)
            
            offset += 130
            
            # render text
            pmap.set_clip_rect(0, 0, w - 80, h)
            pmap.draw_text(self.__label, theme.font_mb_listitem,
                           offset, 20,
                           theme.color_mb_listitem_text)
            pmap.draw_text(self.__sublabel, theme.font_mb_tiny,
                           offset, h - 40,
                           theme.color_mb_listitem_subtext)
            pmap.set_clip_rect()
            
            # render button
            if (self.__file.mimetype.endswith("-folder")):
                btn = theme.mb_item_btn_open
            else:
                btn = theme.mb_item_btn_play
            pmap.draw_pixbuf(btn, w - 60, (h - 42) / 2)
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def connect_button_pressed(self, *args):
    
        print "item: connect_button_pressed"
        
        
    def click_at(self, px, py):
    
        w, h = self.get_size()
        if (self.__is_compact):
            self.emit_event(self.EVENT_ACTIVATED)
        elif (w - 80 <= px <= w):
            self.emit_event(self.EVENT_ACTIVATED)

        #elif (px < 60):
        #    self.__file.bookmarked = not self.__file.bookmarked
            
            
    def tap_and_hold(self, px, py):
    
        self.emit_event(self.EVENT_MENU_OPENED)

