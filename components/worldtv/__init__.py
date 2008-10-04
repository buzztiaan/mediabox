from com import Component, msgs
from WorldTV import WorldTV

import gobject


class Init(Component):

    def __init__(self):
    
        Component.__init__(self)
        gobject.idle_add(self.emit_event, msgs.CORE_EV_DEVICE_ADDED,
                         "worldtv", WorldTV())


def get_classes():

    return [Init]

