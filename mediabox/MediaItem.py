from ui.itemview.Item import Item
from mediabox import thumbnail
from utils import textutils
from theme import theme


class MediaItem(Item):

    EVENT_ACTIVATED = "activated"


    def __init__(self, f, icon):

        self.__size = (560, 100)

        self.__grip_visible = False

        self.__file = f
        self.__icon = icon
        self.__label = textutils.escape_xml(f.name)
        self.__letter = self.__label and unicode(self.__label)[0].upper() or " "
        self.__sublabel = textutils.escape_xml(f.info)

        Item.__init__(self)


    def connect_activated(self, cb, *args):
    
        self._connect(self.EVENT_ACTIVATED, cb, *args)


    def get_file(self):
    
        return self.__file


    def set_letter(self, letter):
    
        self.__letter = letter


    def get_letter(self):
    
        return self.__letter


    def set_icon(self, icon):
    
        self.__icon = icon


    def set_info(self, info):
    
        self.__sublabel = info
        self.invalidate()
        
         
    def set_grip_visible(self, v):
        
        self.__grip_visible = v


    def get_size(self):
    
        return self.__size
        
        
    def set_size(self, w, h):
    
        if (w > 0 and h > 0):
            self.__size = (w, h)


    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        
        if (is_new):
            #print "FULL RENDER", self.__label

            #if (self.is_marked()):
            #    pmap.fill_area(0, 0, w, h, "#ff0000")
            #if (self.is_hilighted()):
            #    pmap.fill_area(0, 0, w, h, "#0000ff")
            #else:
            pmap.fill_area(0, 0, w, h, "#ffffff")

            # render grip
            if (self.__grip_visible):
                pmap.draw_pixbuf(theme.mb_item_grip, 0, 0)
                offset = 32
            else:
                offset = 4
            
            # render icon
            pbuf = thumbnail.render_on_pixbuf(self.__icon, self.__file.mimetype)
            # weird, Fremantle requires me to make a copy of the pixbuf...
            pbuf2 = pbuf.copy()
            pmap.fit_pixbuf(pbuf2, offset, 20, 140, 80)
            del pbuf2

            # render fav star
            if (self.__file.bookmarked):
                icon = theme.mb_item_fav_2
            else:
                icon = theme.mb_item_fav_1
            pmap.draw_pixbuf(icon, offset, 0)
            
            offset += 140
            
            # render text
            pmap.set_clip_rect(0, 0, w - 80, h)
            pmap.draw_text(self.__label, theme.font_mb_tiny, offset, 20, "#000000")
            pmap.draw_text(self.__sublabel, theme.font_mb_tiny, offset, h - 40, "#666666")
            pmap.set_clip_rect()
            
            # render selection frame
            if (self.is_hilighted()):
                pmap.draw_frame(theme.mb_selection_frame, 0, 0, w, h, True,
                                pmap.TOP | pmap.BOTTOM)
            
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
        if (w - 80 <= px <= w):
            self.emit_event(self.EVENT_ACTIVATED)

        elif (px < 60):
            self.__file.bookmarked = not self.__file.bookmarked
