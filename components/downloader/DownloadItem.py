from ui.itemview import Item
from theme import theme

import os
import time


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


    def set_destination(self, dest):
    
        if (dest != self.__destination):
            self.__destination = dest
            self._invalidate_cached_pixmap()


    def set_amount(self, amount, total):
    
        if (amount - self.__amount > 1024):
            self.__amount = amount
            self.__total = total
            self._invalidate_cached_pixmap()


    def __pretty_size(self, s):

        if (s == -1):
            return "?"
            
        if (s > 1024 * 1024 * 1024):
            size = s / float(1024 * 1024 * 1024)
            size_unit = "GiB"
            format = "%0.1f %s"
        elif (s > 1024 * 1024):
            size = s / float(1024 * 1024)
            size_unit = "MiB"
            format = "%0.1f %s"
        elif (s > 1024):
            size = s / float(1024)
            size_unit = "KiB"
            format = "%d %s"
        else:
            size = s
            size_unit = "B"
            format = "%d %s"

        return format % (size, size_unit)


    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            if (self.__total > 0):
                percents = int((self.__amount / float(self.__total)) * 100)
                animation_percents = percents - (percents % 10)
            else:
                percents = 0
                t = int(time.time())
                animation_percents = t % 10

            if (self.__total > 0):
                size = "%s / %s" % (self.__pretty_size(self.__amount),
                                    self.__pretty_size(self.__total))
            else:
                size = self.__pretty_size(self.__amount)

            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            # render animated progress
            pmap.draw_subpixbuf(theme.mb_download_progress,
                                animation_percents * 64, 0,
                                4, (h - 64) / 2, 64, 64)

            pmap.set_clip_rect(0, 0, w - 80, h)
            pmap.draw_text("%s" % self.__destination,
                           theme.font_mb_plain,
                           80, 2, theme.color_list_item_text)
            pmap.draw_text("%s - %s" % (self.__domain, size),
                           theme.font_mb_tiny,
                           80, 30, theme.color_list_item_subtext)
            pmap.set_clip_rect()

            pmap.draw_pixbuf(theme.mb_download_abort,
                             w - 80 + (80 - 42) / 2, (h - 42) / 2)

        #end if

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def click_at(self, px, py):
    
        w, h = self.get_size()
        if (px > w - 80):
            self.emit_event(self.EVENT_CLICKED)

