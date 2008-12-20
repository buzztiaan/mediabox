from com import msgs
from GenericViewer import GenericViewer
from storage import Device
from theme import theme


class FolderViewer(GenericViewer):

    ICON = theme.mb_viewer_folder
    PRIORITY = 0

    def __init__(self):
    
        GenericViewer.__init__(self)
        self.accept_device_types(Device.TYPE_GENERIC)
        self.add_tab("Browser", self._VIEWMODE_BROWSER)
        self.add_tab("Player", self._VIEWMODE_PLAYER_NORMAL)
        self.add_tab("Library", self._VIEWMODE_LIBRARY)


    def show(self):
    
        GenericViewer.show(self)
        
        # search for UPnP devices
        self.emit_event(msgs.SSDP_ACT_SEARCH_DEVICES)

