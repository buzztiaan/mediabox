from GenericViewer import GenericViewer
from storage import Device
from theme import theme


class ImageViewer(GenericViewer):

    ICON = theme.mb_viewer_image
    PRIORITY = 30

    def __init__(self):
    
        GenericViewer.__init__(self)
        self.accept_device_types(Device.TYPE_IMAGE)
        self.add_tab("Browser", self._VIEWMODE_BROWSER)
        self.add_tab("Image", self._VIEWMODE_PLAYER_NORMAL)
        self.add_tab("Info", self._VIEWMODE_PLAYER_NORMAL)

