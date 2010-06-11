from ui.itemview import Item
from theme import theme

import os


class DownloadItem(Item):
    """
    List item for download manager.
    """

    def __init__(self, url, destination):

        self.__url = url
        self.__destination = os.path.basename(destination)
        self.__amount = 0
        self.__total = 0
                
        Item.__init__(self)


    def set_amount(self, amount, total):
    
        self.__amount = amount
        self.__total = total
        self._invalidate_cached_pixmap()        


    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            if (self.__total > 0):
                percents = int((self.__amount / float(self.__total)) * 100)
            else:
                percents = 0

            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_text("%d%%: %s" % (percents, self.__destination),
                           theme.font_mb_plain,
                           12, 2, theme.color_list_item_text)
            pmap.draw_text("%s" % self.__url,
                           theme.font_mb_tiny,
                           12, 30, theme.color_list_item_subtext)
            pmap.set_clip_rect()
        #end if

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def click_at(self, px, py):
    
        w, h = self.get_size()
        if (px > w - 80):
            self.emit_event(self.EVENT_CLICKED)

