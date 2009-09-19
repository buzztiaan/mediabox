from mediabox.MediaViewer import MediaViewer
from RootDevice import RootDevice
from ui.Widget import Widget
from theme import theme


class Navigator(MediaViewer):

    ICON = theme.mb_viewer_audio
    TITLE = "Browser"
    PRIORITY = 0

    def __init__(self):
    
        MediaViewer.__init__(self, RootDevice(), "Navigator", "Player")

