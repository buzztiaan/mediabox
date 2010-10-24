from ui.Widget import Widget
from ui.Label import Label
from theme import theme


class InfoBox(Widget):

    def __init__(self):
    
        self.__cover = None
        self.__cover_scaled = None
        self.__title = ""
        self.__album = ""
        self.__artist = ""
    
        Widget.__init__(self)

        self.__lbl_title = Label("-", theme.font_mb_headline,
                                 theme.color_audio_player_trackinfo_title)
        self.__lbl_title.set_alignment(Label.CENTERED)
        self.add(self.__lbl_title)

        self.__lbl_album = Label("-", theme.font_mb_plain,
                                 theme.color_audio_player_trackinfo_album)
        self.__lbl_album.set_alignment(Label.CENTERED)
        self.add(self.__lbl_album)

        self.__lbl_artist = Label("-", theme.font_mb_plain,
                                  theme.color_audio_player_trackinfo_artist)
        self.__lbl_artist.set_alignment(Label.CENTERED)
        self.add(self.__lbl_artist)
  
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h,
                         theme.color_audio_player_trackinfo_background)
        #screen.fill_area(x, y, w, h, "#000000")
        #screen.draw_frame(theme.mb_selection_frame, x, y, w, h, True)
        
        self.__lbl_title.set_geometry(8, 4, w - 16, 30)
        self.__lbl_album.set_geometry(8, 44, w - 16, 20)
        self.__lbl_artist.set_geometry(8, 74, w - 16, 20)
        
        
    def set_cover(self, pbuf):
    
        self.__cover = pbuf
        
        
    def set_title(self, title):
    
        self.__lbl_title.set_text(title)


    def set_album(self, album):
    
        self.__lbl_album.set_text(album)
        
        
    def set_artist(self, artist):
    
        self.__lbl_artist.set_text(artist)

