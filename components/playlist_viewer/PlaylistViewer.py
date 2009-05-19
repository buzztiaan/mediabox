from mediabox.MediaViewer import MediaViewer
from PlaylistDevice import PlaylistDevice
from theme import theme


class PlaylistViewer(MediaViewer):
    """
    Viewer for playlists.
    """

    ICON = theme.mb_viewer_playlist
    PRIORITY = 5

    def __init__(self):
    
        self.__needs_reload = False
    
        MediaViewer.__init__(self, PlaylistDevice(), "Playlist", "Player")


    def show(self):
    
        MediaViewer.show(self)
        
        if (self.__needs_reload):
            self.get_browser().reload_current_folder()
            self.__needs_reload = False


    def handle_PLAYLIST_ACT_APPEND(self, f):
        
        self.__needs_reload = True

