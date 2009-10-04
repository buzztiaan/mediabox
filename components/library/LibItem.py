from ui.itemview import Item
from mediabox import config
from theme import theme


class LibItem(Item):

    def __init__(self, mediaroot, mtypes):
    
        self.__mediaroot = mediaroot
        self.__mtypes = mtypes
    
        Item.__init__(self)
        
        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            icons = [
                self.__mtypes & config.MEDIA_VIDEO and theme.prefs_video_on
                                                   or  theme.prefs_video_off,
                self.__mtypes & config.MEDIA_AUDIO and theme.prefs_music_on
                                                   or  theme.prefs_music_off,
                self.__mtypes & config.MEDIA_IMAGE and theme.prefs_image_on
                                                   or  theme.prefs_image_off
            ]

            xpos = 20
            for icon in icons:
                pmap.draw_pixbuf(icon, xpos, 0)
                xpos += 64
            #end for
                
            
            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_text(self.__mediaroot, theme.font_mb_listitem,
                           xpos, 10, theme.color_mb_listitem_text)
            pmap.set_clip_rect()            
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)
