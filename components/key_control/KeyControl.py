from com import Component, msgs


class KeyControl(Component):

    def __init__(self):
    
        Component.__init__(self)
        
        
    def handle_event(self, msg, *args):
    
        if (msg == msgs.HWKEY_EV_LEFT):
            self.emit_event(msgs.MEDIA_ACT_PREVIOUS)
            
        elif (msg == msgs.HWKEY_EV_RIGHT):
            self.emit_event(msgs.MEDIA_ACT_NEXT)

        elif (msg == msgs.HWKEY_EV_HEADSET):
            self.emit_event(msgs.MEDIA_ACT_PAUSE)

        elif (msg == msgs.HWKEY_EV_HEADSET_DOUBLE):
            self.emit_event(msgs.MEDIA_ACT_NEXT)

        elif (msg == msgs.HWKEY_EV_HEADSET_TRIPLE):
            self.emit_event(msgs.MEDIA_ACT_PREVIOUS)

