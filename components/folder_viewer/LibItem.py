from ui.ButtonListItem import ButtonListItem
from mediabox import thumbnail
import theme


class LibItem(ButtonListItem):
    """
    List item for library entries.
    """

    BUTTON_REMOVE = "remove"


    _ITEMS_CLOSED = [theme.mb_item_btn_remove]
    _ITEMS_OPEN = []

    _BUTTONS = [BUTTON_REMOVE]


    def __init__(self, f):

        self.__media_types = 7
        self.__icon = f.source_icon
        self.__label = self.escape_xml(f.name)
        self.__fullpath = f.full_path
        self.__sublabel = self.escape_xml(self.__fullpath)        
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_fg_item, theme.color_fg_item_2)
        self.set_font(theme.font_plain)


    def set_media_types(self, mtypes):
    
        self.__media_types = mtypes
        self.invalidate()
        
        
    def get_media_types(self):
    
        return self.__media_types
        
        
    def get_path(self):
    
        return self.__fullpath


    def render_this(self, cnv):
    
        ButtonListItem.render_this(self, cnv)
        #print "render this", self

        print self.__icon
        if (self.__icon):
            w, h = self.get_size()
            cnv.fit_pixbuf(self.__icon, 220, 4, 32, 32)

        self.render_label(cnv, 220, "\t" + self.__label, self.__sublabel)

        x = 4
        for icon_on, icon_off, t in [
                (theme.prefs_video_on, theme.prefs_video_off, 1),
                (theme.prefs_music_on, theme.prefs_music_off, 2),
                (theme.prefs_image_on, theme.prefs_image_off, 4)]:
            icon = (self.__media_types & t) and icon_on or icon_off
            cnv.draw_pixbuf(icon, x, 12)
            x += 64
        #end for
       
        self.render_buttons(cnv)

