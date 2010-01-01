from com import Component, msgs

import gtk


class DSPSemaphore(Component):
    """
    Only one client must access the DSP at a time for playing video. If two
    clients attempt to play a video at the same time, the device will crash.
    This semaphore avoids conflicts between the video player and the video
    thumbnailer.
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

