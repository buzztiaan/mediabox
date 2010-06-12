from ui.itemview import Item
from theme import theme

import os


class DownloadItem(Item):
    """
    List item for download manager.
    """

    def __init__(self, url, destination):

        idx = url.find("://")
        idx2 = url.find("/", idx + 3)
        domain = url[:idx2]
    
        self.__domain = domain
        self.__url = url
        self.__destination = os.path.basename(destination)
        self.__amount = 0
        self.__total = 0
                
        Item.__init__(self)


    def set_amount(self, amount, total):
    
        self.__amount = amount
        self.__total = total
        self._invalidate_cached_pixmap()        


    def __pretty_size(self, s):

        if (s == -1):
            return "?"
            
        if (s > 1024 * 1024 * 1024):
            size = s / float(1024 * 1024 * 1024)
            size_unit = "GB"
        elif (s > 1024 * 1024):
            size = s / float(1024 * 1024)
            size_unit = "MB"
        elif (s > 1024):
            size = s / float(1024)
            size_unit = "KB"
        else:
            size = s
            size_unit = "B"

        return "%0.2f %s" % (size, size_unit)


    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            if (self.__total > 0):
                percents = int((self.__amount / float(self.__total)) * 100)
            else:
                percents = 0

            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            pmap.set_clip_rect(0, 0, w - 80, h)
            pmap.draw_text("%s" % self.__destination,
                           theme.font_mb_plain,
                           12, 2, theme.color_list_item_text)
            pmap.draw_text("%s / %s - %s" % (self.__pretty_size(self.__amount),
                                             self.__pretty_size(self.__total),
                                             self.__domain),
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

