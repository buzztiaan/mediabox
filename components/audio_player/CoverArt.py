from ui.Widget import Widget
from ui.Pixmap import Pixmap
from utils import textutils
from theme import theme



class CoverArt(Widget):

    def __init__(self):
    
        self.__buffer = None
        self.__cover_pbuf = None
        self.__lyrics = ("", 0, 0)
    
        Widget.__init__(self)


    def _reload(self):
    
        self.__render_cover()
        self.__render_lyrics()
        self.render()
        

    def set_size(self, w, h):
    
        old_w, old_h = self.get_size()
        Widget.set_size(self, w, h)
        if ((old_w, old_h) != (w, h)):
            self.__buffer = Pixmap(None, w, h)        
            self.__render_cover()
            self.__render_lyrics()
        #end if


    def render_this(self):
    
        if (not self.__buffer): return
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.copy_buffer(self.__buffer, 0, 0, x, y, w, h)


    def __render_cover(self):

        b_w, b_h = self.__buffer.get_size()
        self.__buffer.fill_area(0, 0, b_w, b_h, theme.color_mb_background)
        if (self.__cover_pbuf):
            self.__buffer.fit_pixbuf(self.__cover_pbuf, 0, 0, b_w, b_h)
        else:
            self.__buffer.fit_pixbuf(theme.mb_unknown_album, 0, 0, b_w, b_h)


    def __render_lyrics(self):
    
        words, hi_from, hi_to = self.__lyrics
        if (not words): return

        b_w, b_h = self.__buffer.get_size()

        if (hi_from > 0 or hi_to < len(words) - 1):
            text = "%s<span color='red'>%s</span>%s" \
                   % (textutils.escape_xml(words[:hi_from]),
                      textutils.escape_xml(words[hi_from:hi_to]),
                      textutils.escape_xml(words[hi_to:]))
        else:
            text = textutils.escape_xml(words)
        
        bx = 5
        by = b_h / 2
        bw = b_w - 10
        bh = b_h / 2 - 10

        self.__buffer.draw_frame(theme.mb_lyrics_box, bx, by, bw, bh, True)
        self.__buffer.draw_formatted_text(text, theme.font_mb_headline,
                                          bx + 8, by + 8, bw - 16, bh - 16,
                                          theme.color_audio_player_lyrics,
                                          self.__buffer.LEFT,
                                          True)        

        
    def set_cover(self, pbuf):
    
        self.__cover_pbuf = pbuf
        self.__render_cover()
        self.render()


    def unset_cover(self):
    
        del self.__cover_pbuf
        self.__cover_pbuf = None
        self.__render_cover()
        self.render()

        
    def set_lyrics(self, text, hi_from, hi_to):
    
        self.__lyrics = (text, hi_from, hi_to)
        self.__render_cover()
        self.__render_lyrics()
        self.render()

