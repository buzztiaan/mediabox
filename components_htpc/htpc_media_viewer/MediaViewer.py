from com import msgs
from RootDevice import RootDevice
from mediabox.MediaViewer import MediaViewer as _MediaViewer
from mediabox import viewmodes
from theme import theme


class MediaViewer(_MediaViewer):

    ICON = theme.mb_viewer_folder
    PRIORITY = 0

    def __init__(self):

        _MediaViewer.__init__(self, RootDevice(), "Browser", "Media",
                              show_sliders = False)

        self.get_browser().connect_folder_opened(self.__on_open_folder)


    def show(self):
    
        _MediaViewer.show(self)
        
        # search for UPnP devices
        self.emit_message(msgs.SSDP_ACT_SEARCH_DEVICES)



    def __on_open_folder(self, f):
    
        self.emit_message(msgs.HTPC_EV_FOLDER_OPENED, f)

