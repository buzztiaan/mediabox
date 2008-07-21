from com import Viewer, msgs
import theme


class PlaylistViewer(Viewer):

    ICON = theme.mb_viewer_playlist
    ICON_ACTIVE = theme.mb_viewer_playlist_active
    PRIORITY = 5

    def __init__(self):
    
        Viewer.__init__(self)
        
        
        
    def handle_event(self, msg, *args):
    
        if (msg == msgs.PLAYLIST_ACT_APPEND):
            f = args[0]
            print "Adding to playlist: %s" % f.name

