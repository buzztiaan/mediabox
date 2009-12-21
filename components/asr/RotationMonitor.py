from com import Component, msgs
import platforms



class RotationMonitor(Component):
    """
    Monitor for detecting rotating the device.
    Emits ASR_EV_PORTRAIT and ASR_EV_LANDSCAPE events.
    """
    
    def __init__(self):
    
        Component.__init__(self)

        #bus = platforms.get_system_bus()
        #obj = bus.get_object("com.nokia.mce", "/com/nokia/mce/signal")
        #obj.connect_to_signal("sig_device_orientation_ind",
        #                      self.__on_rotate)
                                 
                                 
    def __on_rotate(self, orientation, stand_mode, face_mode,
                    axis1, axis2, axis3):
    
        if (orientation in ("landscape", "landscape (inverted)")):
            self.emit_message(msgs.ASR_EV_LANDSCAPE)
            
        elif (orientation == "portrait"):
            self.emit_message(msgs.ASR_EV_PORTRAIT)

