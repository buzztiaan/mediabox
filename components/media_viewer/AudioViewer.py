from mediabox.MediaViewer import MediaViewer
from AudioDevice import AudioDevice
from theme import theme


class AudioViewer(MediaViewer):

    ICON = theme.mb_viewer_audio
    PRIORITY = 20

    def __init__(self):
    
        MediaViewer.__init__(self, AudioDevice(), "Browser", "Track")

