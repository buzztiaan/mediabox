from com import Component, msgs
from YouTube import YouTube
from Prefs import Prefs

import gobject

class Init(Component):

    def __init__(self):
    
        Component.__init__(self)
        gobject.idle_add(self.emit_event, msgs.CORE_EV_DEVICE_ADDED,
                         "www.youtube.com", YouTube())



def get_classes():

    return [Init, Prefs]

