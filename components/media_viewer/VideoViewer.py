from mediabox.MediaViewer import MediaViewer
from VideoDevice import VideoDevice
from storage import Device
from theme import theme


class VideoViewer(MediaViewer):

    ICON = theme.mb_viewer_video
    PRIORITY = 10

    def __init__(self):
    
        MediaViewer.__init__(self, VideoDevice(), "Browser", "Videos")

