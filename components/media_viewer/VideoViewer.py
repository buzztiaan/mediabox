from GenericViewer import GenericViewer
from storage import Device
from theme import theme


class VideoViewer(GenericViewer):

    ICON = theme.mb_viewer_video
    PRIORITY = 10

    def __init__(self):
    
        GenericViewer.__init__(self)
        self.accept_device_types(Device.TYPE_VIDEO)
        self.add_tab("Browser", self._VIEWMODE_BROWSER)
        self.add_tab("Video", self._VIEWMODE_PLAYER_NORMAL)

