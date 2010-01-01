from com import Dialog, msgs
from mediabox.FMScale import FMScale
from ui.CheckBox import CheckBox


class FMTXDialog(Dialog):
    """
    Dialog for setting up the FM transmitter.
    """

    def __init__(self):
    
        Dialog.__init__(self)
        
        self.__fmscale = FMScale()
        self.add(self.__fmscale)
        
        self.__chk_fmtx = CheckBox()
        self.add(self.__chk_fmtx)
        
        
    
    def render_this(self):
    
        w, h = self.get_size()
        
        self.__fmscale.set_geometry(0, 0, w, h - 80)
        self.__chk_fmtx.set_geometry(0, h - 80, w, 80)

