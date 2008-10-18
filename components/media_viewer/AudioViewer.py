from GenericViewer import GenericViewer
from storage import Device
import theme


class AudioViewer(GenericViewer):

    ICON = theme.mb_viewer_audio
    PRIORITY = 20

    def __init__(self):
    
        GenericViewer.__init__(self)
        self.accept_device_types(Device.TYPE_AUDIO)
        self.add_tab("Browser", self._VIEWMODE_BROWSER)
        self.add_tab("Track Info", self._VIEWMODE_PLAYER_NORMAL)

