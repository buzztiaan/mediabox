from com import Component, msgs

import gtk


class DSPSemaphore(Component):
    """
    This semaphore avoids DSP conflicts between the video player and the video
    thumbnailer. Conflicts that may crash the device.
    """

    def __init__(self):
    
        self.__is_locked = False
    
        Component.__init__(self)
        
        
    def handle_VIDEOPLAYER_SVC_LOCK_DSP(self):
    
        while (self.__is_locked):
            gtk.main_iteration()
        self.__is_locked = True


    def handle_VIDEOPLAYER_SVC_RELEASE_DSP(self):
    
        self.__is_locked = False

