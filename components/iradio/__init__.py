from com import Component, msgs
from IRadio import IRadio

import gobject

class Init(Component):

    def __init__(self):
    
        Component.__init__(self)
        gobject.idle_add(self.emit_event, msgs.CORE_EV_DEVICE_ADDED,
                         "iradio", IRadio())



def get_classes():

    return [Init]

